from __future__ import annotations

import pandas as pd

from backend.app.services.matching.matcher import (
    SettlementMatcher,
)


class SmartReconciliationEngine:
    """
    Unified reconciliation engine.

    Strategy:

    1. Try deterministic exact reconciliation.
    2. If no exact settlement exists, use intelligent matching.
    3. Use confidence and candidate margin to classify
       the intelligent result.
    4. Never silently accept weak matches.
    """

    def __init__(
        self,
        orders: pd.DataFrame,
        payments: pd.DataFrame,
        settlements: pd.DataFrame,
    ):
        self.orders = orders.copy()
        self.payments = payments.copy()
        self.settlements = settlements.copy()

        self._normalize_data()

        self.matcher = SettlementMatcher(
            self.settlements
        )

    def _normalize_data(self) -> None:
        """Normalize dates, identifiers and amounts."""

        self.orders["order_date"] = pd.to_datetime(
            self.orders["order_date"]
        )

        self.payments["payment_date"] = pd.to_datetime(
            self.payments["payment_date"]
        )

        self.settlements["settlement_date"] = pd.to_datetime(
            self.settlements["settlement_date"]
        )

        self.orders["order_amount"] = (
            self.orders["order_amount"].astype(float)
        )

        self.payments["payment_amount"] = (
            self.payments["payment_amount"].astype(float)
        )

        for column in [
            "gross_amount",
            "fee",
            "tax",
            "net_amount",
        ]:
            self.settlements[column] = (
                self.settlements[column].astype(float)
            )

        for dataframe, columns in [
            (
                self.orders,
                ["order_id", "customer_id"],
            ),
            (
                self.payments,
                ["payment_id", "order_id", "customer_id"],
            ),
            (
                self.settlements,
                [
                    "payment_id",
                    "merchant_reference",
                    "customer_id",
                    "settlement_id",
                ],
            ),
        ]:
            for column in columns:
                dataframe[column] = (
                    dataframe[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

    def _find_order(
        self,
        order_id: str,
    ) -> pd.Series | None:
        matches = self.orders[
            self.orders["order_id"] == order_id
        ]

        if matches.empty:
            return None

        return matches.iloc[0]

    def _find_exact_settlements(
        self,
        payment_id: str,
    ) -> pd.DataFrame:
        return self.settlements[
            self.settlements["payment_id"] == payment_id
        ]

    @staticmethod
    def _amount_matches(
        payment_amount: float,
        settlement_amount: float,
        tolerance: float = 0.01,
    ) -> bool:
        return (
            abs(
                payment_amount
                - settlement_amount
            )
            <= tolerance
        )

    @staticmethod
    def _settlement_is_on_time(
        payment_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        maximum_days: int = 3,
    ) -> bool:
        delay = (
            settlement_date
            - payment_date
        ).days

        return delay <= maximum_days

    @staticmethod
    def _base_result(
        payment: pd.Series,
    ) -> dict:
        return {
            "payment_id": payment["payment_id"],
            "order_id": payment["order_id"],
            "payment_amount": float(
                payment["payment_amount"]
            ),
            "settlement_id": None,
            "settlement_amount": None,
            "difference_amount": None,
            "status": None,
            "exception_type": "none",
            "decision_source": None,
            "confidence": 0.0,
            "matching_margin": 0.0,
            "explanation": "",
        }

    def reconcile_payment(
        self,
        payment: pd.Series,
    ) -> dict:

        result = self._base_result(
            payment
        )

        # --------------------------------------------------
        # 1. Validate order
        # --------------------------------------------------

        order = self._find_order(
            payment["order_id"]
        )

        if order is None:
            result.update(
                {
                    "status": "EXCEPTION",
                    "exception_type": "missing_order",
                    "decision_source": "DETERMINISTIC",
                    "confidence": 1.0,
                    "explanation": (
                        "Payment references an "
                        "order that does not exist."
                    ),
                }
            )

            return result

        # --------------------------------------------------
        # 2. Try exact settlement match
        # --------------------------------------------------

        exact_settlements = (
            self._find_exact_settlements(
                payment["payment_id"]
            )
        )

        # --------------------------------------------------
        # 3. No exact settlement
        # --------------------------------------------------

        if exact_settlements.empty:

            match_result = self.matcher.match(
                payment
            )

            result["decision_source"] = (
                "INTELLIGENT_MATCHING"
            )

            result["confidence"] = (
                match_result["confidence"]
            )

            result["matching_margin"] = (
                match_result.get(
                    "margin",
                    0.0,
                )
            )

            candidate_id = (
                match_result["candidate"]
            )

            result["settlement_id"] = (
                candidate_id
            )

            # High-confidence recovery
            if (
                match_result["status"]
                == "HIGH_CONFIDENCE"
                and candidate_id
            ):

                candidate_rows = self.settlements[
                    self.settlements["settlement_id"]
                    == candidate_id
                ]

                if not candidate_rows.empty:

                    candidate = (
                        candidate_rows.iloc[0]
                    )

                    settlement_amount = float(
                        candidate["gross_amount"]
                    )

                    difference = round(
                        float(
                            payment["payment_amount"]
                        )
                        - settlement_amount,
                        2,
                    )

                    result.update(
                        {
                            "status": "MATCHED",
                            "settlement_amount": (
                                settlement_amount
                            ),
                            "difference_amount": (
                                difference
                            ),
                            "exception_type": "none",
                            "explanation": (
                                "No exact payment ID "
                                "match was found, but "
                                "the settlement was "
                                "recovered using "
                                "high-confidence "
                                "intelligent matching."
                            ),
                        }
                    )

                    return result

            # Medium confidence
            if match_result["status"] == "REVIEW":

                result.update(
                    {
                        "status": "REVIEW",
                        "exception_type": (
                            "ambiguous_match"
                        ),
                        "explanation": (
                            "A plausible settlement "
                            "candidate was found, "
                            "but the evidence is "
                            "not strong enough for "
                            "automatic reconciliation."
                        ),
                    }
                )

                return result

            # No reliable candidate
            result.update(
                {
                    "status": "UNRESOLVED",
                    "exception_type": (
                        "insufficient_evidence"
                    ),
                    "explanation": (
                        "No sufficiently reliable "
                        "settlement match could "
                        "be established."
                    ),
                }
            )

            return result

        # --------------------------------------------------
        # 4. Multiple exact settlements
        # --------------------------------------------------

        if len(exact_settlements) > 1:

            settlement_ids = ", ".join(
                exact_settlements[
                    "settlement_id"
                ]
                .astype(str)
                .tolist()
            )

            result.update(
                {
                    "status": "EXCEPTION",
                    "exception_type": (
                        "duplicate_settlement"
                    ),
                    "decision_source": (
                        "DETERMINISTIC"
                    ),
                    "confidence": 1.0,
                    "settlement_id": (
                        settlement_ids
                    ),
                    "explanation": (
                        f"Multiple settlements "
                        f"were found: "
                        f"{settlement_ids}"
                    ),
                }
            )

            return result

        # --------------------------------------------------
        # 5. Validate single exact settlement
        # --------------------------------------------------

        settlement = exact_settlements.iloc[0]

        settlement_amount = float(
            settlement["gross_amount"]
        )

        difference = round(
            float(
                payment["payment_amount"]
            )
            - settlement_amount,
            2,
        )

        result.update(
            {
                "settlement_id": str(
                    settlement["settlement_id"]
                ),
                "settlement_amount": (
                    settlement_amount
                ),
                "difference_amount": (
                    difference
                ),
                "decision_source": (
                    "DETERMINISTIC"
                ),
            }
        )

        # --------------------------------------------------
        # 6. Amount mismatch
        # --------------------------------------------------

        if not self._amount_matches(
            float(payment["payment_amount"]),
            settlement_amount,
        ):

            result.update(
                {
                    "status": "EXCEPTION",
                    "exception_type": (
                        "amount_mismatch"
                    ),
                    "confidence": 1.0,
                    "explanation": (
                        "Payment amount and "
                        "settlement gross amount "
                        "do not match."
                    ),
                }
            )

            return result

        # --------------------------------------------------
        # 7. Settlement delay
        # --------------------------------------------------

        if not self._settlement_is_on_time(
            payment["payment_date"],
            settlement["settlement_date"],
        ):

            delay = (
                settlement["settlement_date"]
                - payment["payment_date"]
            ).days

            result.update(
                {
                    "status": "EXCEPTION",
                    "exception_type": (
                        "settlement_delay"
                    ),
                    "confidence": 1.0,
                    "explanation": (
                        f"Settlement occurred "
                        f"{delay} days after "
                        f"payment."
                    ),
                }
            )

            return result

        # --------------------------------------------------
        # 8. Exact successful match
        # --------------------------------------------------

        result.update(
            {
                "status": "MATCHED",
                "confidence": 1.0,
                "explanation": (
                    "Payment, order, and settlement "
                    "records were successfully "
                    "reconciled using deterministic "
                    "matching."
                ),
            }
        )

        return result

    def reconcile(self) -> pd.DataFrame:

        results = []

        for _, payment in (
            self.payments.iterrows()
        ):

            result = self.reconcile_payment(
                payment
            )

            results.append(
                result
            )

        return pd.DataFrame(results)