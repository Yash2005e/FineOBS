from __future__ import annotations

import pandas as pd

from backend.app.services.matching.matcher import (
    SettlementMatcher,
)


class IntelligentReconciliationEngine:

    def __init__(
        self,
        payments: pd.DataFrame,
        settlements: pd.DataFrame,
    ):
        self.payments = payments.copy()
        self.settlements = settlements.copy()

        self.payments["payment_date"] = pd.to_datetime(
            self.payments["payment_date"]
        )

        self.settlements["settlement_date"] = pd.to_datetime(
            self.settlements["settlement_date"]
        )

        self.matcher = SettlementMatcher(
            self.settlements
        )

    def reconcile(self) -> pd.DataFrame:

        results = []

        for _, payment in self.payments.iterrows():

            result = self.matcher.match(
                payment
            )

            candidate = result["candidate"]

            settlement = None

            if candidate is not None:

                matches = self.settlements[
                    self.settlements["settlement_id"]
                    == candidate
                ]

                if not matches.empty:
                    settlement = matches.iloc[0]

            results.append(
                {
                    "payment_id": payment["payment_id"],
                    "order_id": payment["order_id"],
                    "matched_settlement_id": candidate,
                    "matching_status": result["status"],
                    "confidence": result["confidence"],
                    "matching_margin": result.get(
                        "margin",
                        0.0,
                    ),
                    "payment_amount": float(
                        payment["payment_amount"]
                    ),
                    "settlement_amount": (
                        float(
                            settlement["gross_amount"]
                        )
                        if settlement is not None
                        else None
                    ),
                }
            )

        return pd.DataFrame(results)