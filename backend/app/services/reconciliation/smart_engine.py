from __future__ import annotations

import pandas as pd

from backend.app.services.agents.controller import (
    FinanceController,
)
from backend.app.services.matching.matcher import (
    SettlementMatcher,
)


class SmartReconciliationEngine:
    """
    Unified FineOBS reconciliation engine.

    Workflow:

    1. Validate the referenced order.
    2. Try deterministic exact settlement matching.
    3. If exact matching fails, use intelligent matching.
    4. Use confidence and candidate margin to classify
       the intelligent result.
    5. Send REVIEW cases to the AI verification layer.
    6. Convert AI decisions into FineOBS statuses.
    7. Keep uncertain cases unresolved.

    FineOBS statuses:

        MATCHED
        EXCEPTION
        REVIEW
        UNRESOLVED

    Decision sources:

        DETERMINISTIC
        INTELLIGENT_MATCHING
        AI_VERIFICATION
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

        self.controller = FinanceController()

    # ==================================================
    # DATA NORMALIZATION
    # ==================================================

    def _normalize_data(self) -> None:
        """Normalize dates, identifiers, and amounts."""

        # Dates
        self.orders["order_date"] = pd.to_datetime(
            self.orders["order_date"]
        )

        self.payments["payment_date"] = pd.to_datetime(
            self.payments["payment_date"]
        )

        self.settlements["settlement_date"] = (
            pd.to_datetime(
                self.settlements["settlement_date"]
            )
        )

        # Numeric values
        self.orders["order_amount"] = (
            self.orders["order_amount"]
            .astype(float)
        )

        self.payments["payment_amount"] = (
            self.payments["payment_amount"]
            .astype(float)
        )

        for column in [
            "gross_amount",
            "fee",
            "tax",
            "net_amount",
        ]:
            self.settlements[column] = (
                self.settlements[column]
                .astype(float)
            )

        # String identifiers
        dataframes_and_columns = [
            (
                self.orders,
                [
                    "order_id",
                    "customer_id",
                ],
            ),
            (
                self.payments,
                [
                    "payment_id",
                    "order_id",
                    "customer_id",
                ],
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
        ]

        for dataframe, columns in (
            dataframes_and_columns
        ):
            for column in columns:
                dataframe[column] = (
                    dataframe[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

    # ==================================================
    # ORDER LOOKUP
    # ==================================================

    def _find_order(
        self,
        order_id: str,
    ) -> pd.Series | None:
        """Find the order referenced by a payment."""

        matches = self.orders[
            self.orders["order_id"]
            == order_id
        ]

        if matches.empty:
            return None

        return matches.iloc[0]

    # ==================================================
    # EXACT SETTLEMENT LOOKUP
    # ==================================================

    def _find_exact_settlements(
        self,
        payment_id: str,
    ) -> pd.DataFrame:
        """Find settlements with an exact payment ID."""

        return self.settlements[
            self.settlements["payment_id"]
            == payment_id
        ]

    # ==================================================
    # VALIDATION HELPERS
    # ==================================================

    @staticmethod
    def _amount_matches(
        payment_amount: float,
        settlement_amount: float,
        tolerance: float = 0.01,
    ) -> bool:
        """Check whether payment and settlement amounts match."""

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
        """Check whether settlement is within the expected window."""

        delay = (
            settlement_date
            - payment_date
        ).days

        return delay <= maximum_days

    # ==================================================
    # BASE RESULT
    # ==================================================

    @staticmethod
    def _base_result(
        payment: pd.Series,
    ) -> dict:
        """Create the standard result structure."""

        return {
            "payment_id": payment[
                "payment_id"
            ],
            "order_id": payment[
                "order_id"
            ],
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
            "ai_recommendation": None,
            "explanation": "",
        }

    # ==================================================
    # CANDIDATE SETTLEMENT LOOKUP
    # ==================================================

    def _get_candidate_settlement(
        self,
        candidate_id: str | None,
    ) -> pd.Series | None:
        """
        Find the settlement row selected by the
        intelligent matching engine.
        """

        if not candidate_id:
            return None

        matches = self.settlements[
            self.settlements["settlement_id"]
            == candidate_id
        ]

        if matches.empty:
            return None

        return matches.iloc[0]

    # ==================================================
    # SINGLE PAYMENT RECONCILIATION
    # ==================================================

    def reconcile_payment(
        self,
        payment: pd.Series,
    ) -> dict:
        """Reconcile one payment."""

        result = self._base_result(
            payment
        )

        payment_id = payment[
            "payment_id"
        ]

        order_id = payment[
            "order_id"
        ]

        payment_amount = float(
            payment[
                "payment_amount"
            ]
        )

        # --------------------------------------------------
        # STEP 1: Validate order
        # --------------------------------------------------

        order = self._find_order(
            order_id
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
        # STEP 2: Exact settlement lookup
        # --------------------------------------------------

        exact_settlements = (
            self._find_exact_settlements(
                payment_id
            )
        )

        # ==================================================
        # BRANCH A: NO EXACT SETTLEMENT
        # ==================================================

        if exact_settlements.empty:

            # Run intelligent matching.
            match_result = self.matcher.match(
                payment
            )

            result.update(
                {
                    "decision_source": (
                        "INTELLIGENT_MATCHING"
                    ),
                    "confidence": (
                        match_result.get(
                            "confidence",
                            0.0,
                        )
                    ),
                    "matching_margin": (
                        match_result.get(
                            "margin",
                            0.0,
                        )
                    ),
                }
            )

            candidate_id = (
                match_result.get(
                    "candidate"
                )
            )

            result["settlement_id"] = (
                candidate_id
            )

            candidate = (
                self._get_candidate_settlement(
                    candidate_id
                )
            )

            # --------------------------------------------------
            # No candidate
            # --------------------------------------------------

            if candidate is None:

                result.update(
                    {
                        "status": "UNRESOLVED",
                        "exception_type": (
                            "insufficient_evidence"
                        ),
                        "explanation": (
                            "No reliable settlement "
                            "candidate could be identified "
                            "for this payment."
                        ),
                    }
                )

                return result

            # --------------------------------------------------
            # Candidate details
            # --------------------------------------------------

            settlement_amount = float(
                candidate[
                    "gross_amount"
                ]
            )

            difference = round(
                payment_amount
                - settlement_amount,
                2,
            )

            result.update(
                {
                    "settlement_amount": (
                        settlement_amount
                    ),
                    "difference_amount": (
                        difference
                    ),
                }
            )

            # ==================================================
            # HIGH-CONFIDENCE INTELLIGENT MATCH
            # ==================================================

            if (
                match_result["status"]
                == "HIGH_CONFIDENCE"
            ):

                # A high similarity score does not override
                # a financial amount discrepancy.
                if not self._amount_matches(
                    payment_amount,
                    settlement_amount,
                ):

                    result.update(
                        {
                            "status": "EXCEPTION",
                            "exception_type": (
                                "amount_mismatch"
                            ),
                            "explanation": (
                                "A high-confidence "
                                "candidate was found, "
                                "but payment and "
                                "settlement amounts "
                                "do not reconcile."
                            ),
                        }
                    )

                    return result

                result.update(
                    {
                        "status": "MATCHED",
                        "exception_type": "none",
                        "explanation": (
                            "No exact payment ID "
                            "match was available, "
                            "but the settlement "
                            "was recovered using "
                            "high-confidence "
                            "intelligent matching."
                        ),
                    }
                )

                return result

            # ==================================================
            # REVIEW → AI VERIFICATION
            # ==================================================

            if (
                match_result["status"]
                == "REVIEW"
            ):

                verification = (
                    self.controller.verify_case(
                        payment=payment,
                        settlement=candidate,
                        match_result=match_result,
                    )
                )

                decision = verification[
                    "decision"
                ]

                # Convert AI terminology into
                # FineOBS status terminology.
                decision_to_status = {
                    "AUTO_RECONCILE": "MATCHED",
                    "HUMAN_REVIEW": "REVIEW",
                    "UNRESOLVED": "UNRESOLVED",
                }

                final_status = (
                    decision_to_status.get(
                        decision.decision,
                        "REVIEW",
                    )
                )

                result.update(
                    {
                        "status": final_status,

                        "exception_type": (
                            decision.exception_type
                        ),

                        "confidence": (
                            decision.confidence
                        ),

                        "decision_source": (
                            "AI_VERIFICATION"
                        ),

                        "ai_recommendation": (
                            decision.recommended_action
                        ),

                        "explanation": (
                            decision.explanation
                        ),
                    }
                )

                return result

            # ==================================================
            # UNRESOLVED
            # ==================================================

            result.update(
                {
                    "status": "UNRESOLVED",
                    "exception_type": (
                        "insufficient_evidence"
                    ),
                    "explanation": (
                        "The intelligent matching "
                        "engine could not produce "
                        "a sufficiently reliable "
                        "candidate."
                    ),
                }
            )

            return result

        # ==================================================
        # BRANCH B: MULTIPLE EXACT SETTLEMENTS
        # ==================================================

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
                        f"Multiple settlement "
                        f"records were found "
                        f"for payment "
                        f"{payment_id}: "
                        f"{settlement_ids}"
                    ),
                }
            )

            return result

        # ==================================================
        # BRANCH C: ONE EXACT SETTLEMENT
        # ==================================================

        settlement = (
            exact_settlements.iloc[0]
        )

        settlement_id = str(
            settlement[
                "settlement_id"
            ]
        )

        settlement_amount = float(
            settlement[
                "gross_amount"
            ]
        )

        difference = round(
            payment_amount
            - settlement_amount,
            2,
        )

        result.update(
            {
                "settlement_id": (
                    settlement_id
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
        # Amount mismatch
        # --------------------------------------------------

        if not self._amount_matches(
            payment_amount,
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
        # Settlement delay
        # --------------------------------------------------

        payment_date = payment[
            "payment_date"
        ]

        settlement_date = (
            settlement[
                "settlement_date"
            ]
        )

        if not self._settlement_is_on_time(
            payment_date,
            settlement_date,
        ):

            delay = (
                settlement_date
                - payment_date
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

        # ==================================================
        # SUCCESSFUL EXACT MATCH
        # ==================================================

        result.update(
            {
                "status": "MATCHED",
                "exception_type": "none",
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

    # ==================================================
    # FULL BATCH RECONCILIATION
    # ==================================================

    def reconcile(self) -> pd.DataFrame:
        """Reconcile every payment in the batch."""

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

        return pd.DataFrame(
            results
        )