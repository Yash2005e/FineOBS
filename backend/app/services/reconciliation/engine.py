from __future__ import annotations

import pandas as pd

from backend.app.services.matching.matcher import (
    SettlementMatcher,
)


class ReconciliationEngine:
    """
    Deterministic baseline reconciliation engine.

    Responsibilities:
    - Normalize financial records
    - Match payments with orders
    - Match payments with settlements
    - Detect reconciliation exceptions
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
        """Normalize dates, amounts, and identifiers."""

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

        self.orders["order_id"] = (
            self.orders["order_id"]
            .astype(str)
            .str.strip()
        )

        self.payments["payment_id"] = (
            self.payments["payment_id"]
            .astype(str)
            .str.strip()
        )

        self.payments["order_id"] = (
            self.payments["order_id"]
            .astype(str)
            .str.strip()
        )

        self.payments["customer_id"] = (
            self.payments["customer_id"]
            .astype(str)
            .str.strip()
        )

        self.settlements["payment_id"] = (
            self.settlements["payment_id"]
            .astype(str)
            .str.strip()
        )

        self.settlements["merchant_reference"] = (
            self.settlements["merchant_reference"]
            .astype(str)
            .str.strip()
        )

        self.settlements["customer_id"] = (
            self.settlements["customer_id"]
            .astype(str)
            .str.strip()
        )

    def _find_settlements(
        self,
        payment_id: str,
    ) -> pd.DataFrame:
        """Return all settlements for a payment."""

        return self.settlements[
            self.settlements["payment_id"] == payment_id
        ]

    def _find_order(
        self,
        order_id: str,
    ) -> pd.Series | None:
        """Return the corresponding order."""

        matches = self.orders[
            self.orders["order_id"] == order_id
        ]

        if matches.empty:
            return None

        return matches.iloc[0]

    @staticmethod
    def _validate_amount(
        payment_amount: float,
        settlement_amount: float,
        tolerance: float = 0.01,
    ) -> bool:
        """Check whether two amounts reconcile."""

        return (
            abs(
                payment_amount
                - settlement_amount
            )
            <= tolerance
        )

    @staticmethod
    def _check_settlement_delay(
        payment_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
        maximum_days: int = 3,
    ) -> bool:
        """Check whether settlement happened within the expected window."""

        delay = (
            settlement_date - payment_date
        ).days

        return delay <= maximum_days

    def reconcile(self) -> pd.DataFrame:
        """
        Reconcile every payment against its order
        and settlement records.
        """

        results = []

        for _, payment in self.payments.iterrows():

            payment_id = payment["payment_id"]
            order_id = payment["order_id"]
            payment_amount = float(
                payment["payment_amount"]
            )

            order = self._find_order(
                order_id
            )

            settlements = self._find_settlements(
                payment_id
            )

            # ------------------------------------------
            # Missing order
            # ------------------------------------------

            if order is None:
                results.append(
                    {
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "settlement_id": None,
                        "status": "EXCEPTION",
                        "exception_type": "missing_order",
                        "payment_amount": payment_amount,
                        "settlement_amount": None,
                        "difference_amount": None,
                        "confidence": 1.0,
                        "explanation": (
                            "Payment references an "
                            "order that does not exist."
                        ),
                    }
                )

                continue

            # ------------------------------------------
            # Missing settlement
            # ------------------------------------------

            if settlements.empty:
                results.append(
                    {
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "settlement_id": None,
                        "status": "EXCEPTION",
                        "exception_type": "missing_settlement",
                        "payment_amount": payment_amount,
                        "settlement_amount": None,
                        "difference_amount": None,
                        "confidence": 1.0,
                        "explanation": (
                            "No settlement record was "
                            "found for this payment."
                        ),
                    }
                )

                continue

            # ------------------------------------------
            # Duplicate settlements
            # ------------------------------------------

            if len(settlements) > 1:

                settlement_ids = ", ".join(
                    settlements[
                        "settlement_id"
                    ]
                    .astype(str)
                    .tolist()
                )

                results.append(
                    {
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "settlement_id": settlement_ids,
                        "status": "EXCEPTION",
                        "exception_type": (
                            "duplicate_settlement"
                        ),
                        "payment_amount": payment_amount,
                        "settlement_amount": None,
                        "difference_amount": None,
                        "confidence": 1.0,
                        "explanation": (
                            f"Multiple settlements "
                            f"found: {settlement_ids}"
                        ),
                    }
                )

                continue

            # ------------------------------------------
            # Single settlement
            # ------------------------------------------

            settlement = settlements.iloc[0]

            settlement_id = str(
                settlement["settlement_id"]
            )

            gross_amount = float(
                settlement["gross_amount"]
            )

            difference = round(
                payment_amount
                - gross_amount,
                2,
            )

            # ------------------------------------------
            # Amount mismatch
            # ------------------------------------------

            if not self._validate_amount(
                payment_amount,
                gross_amount,
            ):
                results.append(
                    {
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "settlement_id": settlement_id,
                        "status": "EXCEPTION",
                        "exception_type": (
                            "amount_mismatch"
                        ),
                        "payment_amount": payment_amount,
                        "settlement_amount": gross_amount,
                        "difference_amount": difference,
                        "confidence": 1.0,
                        "explanation": (
                            "Payment amount and "
                            "settlement gross amount "
                            "do not match."
                        ),
                    }
                )

                continue

            # ------------------------------------------
            # Settlement delay
            # ------------------------------------------

            payment_date = payment["payment_date"]
            settlement_date = (
                settlement["settlement_date"]
            )

            if not self._check_settlement_delay(
                payment_date,
                settlement_date,
            ):

                delay = (
                    settlement_date
                    - payment_date
                ).days

                results.append(
                    {
                        "payment_id": payment_id,
                        "order_id": order_id,
                        "settlement_id": settlement_id,
                        "status": "EXCEPTION",
                        "exception_type": (
                            "settlement_delay"
                        ),
                        "payment_amount": payment_amount,
                        "settlement_amount": gross_amount,
                        "difference_amount": 0.0,
                        "confidence": 1.0,
                        "explanation": (
                            f"Settlement occurred "
                            f"{delay} days after "
                            f"payment."
                        ),
                    }
                )

                continue

            # ------------------------------------------
            # Successful reconciliation
            # ------------------------------------------

            results.append(
                {
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "settlement_id": settlement_id,
                    "status": "MATCHED",
                    "exception_type": "none",
                    "payment_amount": payment_amount,
                    "settlement_amount": gross_amount,
                    "difference_amount": 0.0,
                    "confidence": 1.0,
                    "explanation": (
                        "Payment, order, and settlement "
                        "records successfully reconciled."
                    ),
                }
            )

        return pd.DataFrame(results)