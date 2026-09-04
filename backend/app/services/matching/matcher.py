from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from rapidfuzz.fuzz import ratio


@dataclass
class MatchCandidate:
    settlement_id: str
    score: float
    reference_similarity: float
    amount_similarity: float
    customer_similarity: float
    date_similarity: float


class SettlementMatcher:
    """
    Finds the most likely settlement for a payment
    using multiple independent matching signals.
    """

    def __init__(
        self,
        settlements: pd.DataFrame,
    ):
        self.settlements = settlements.copy()

        self.settlements["settlement_date"] = (
            pd.to_datetime(
                self.settlements["settlement_date"]
            )
        )

    @staticmethod
    def normalize_reference(
        value: object,
    ) -> str:
        """Normalize references before comparison."""

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "")
            .replace(" ", "")
        )

    @staticmethod
    def reference_similarity(
        payment_reference: str,
        settlement_reference: str,
    ) -> float:
        """Calculate normalized fuzzy reference similarity."""

        payment_reference = (
            SettlementMatcher.normalize_reference(
                payment_reference
            )
        )

        settlement_reference = (
            SettlementMatcher.normalize_reference(
                settlement_reference
            )
        )

        if (
            not payment_reference
            or not settlement_reference
        ):
            return 0.0

        return ratio(
            payment_reference,
            settlement_reference,
        ) / 100.0

    @staticmethod
    def amount_similarity(
        payment_amount: float,
        settlement_amount: float,
    ) -> float:
        """Calculate relative amount similarity."""

        if payment_amount <= 0:
            return 0.0

        difference = abs(
            payment_amount
            - settlement_amount
        )

        relative_difference = (
            difference / payment_amount
        )

        return max(
            0.0,
            1.0 - relative_difference,
        )

    @staticmethod
    def customer_similarity(
        payment_customer: object,
        settlement_customer: object,
    ) -> float:
        """Return 1.0 for exact customer match."""

        if (
            str(payment_customer).strip()
            == str(settlement_customer).strip()
        ):
            return 1.0

        return 0.0

    @staticmethod
    def date_similarity(
        payment_date: pd.Timestamp,
        settlement_date: pd.Timestamp,
    ) -> float:
        """
        Calculate date similarity.

        Same day = 1.0.
        Similarity decreases linearly up to 7 days.
        """

        day_difference = abs(
            (
                settlement_date
                - payment_date
            ).total_seconds()
        ) / 86400

        return max(
            0.0,
            1.0 - (
                day_difference / 7.0
            ),
        )

    def generate_candidate_pool(
        self,
        payment: pd.Series,
    ) -> pd.DataFrame:
        """
        Reduce the search space before detailed scoring.

        A settlement enters the candidate pool when it has
        at least one strong matching signal:
        - same customer
        - similar amount
        - similar merchant reference
        """

        candidates = self.settlements.copy()

        payment_customer = str(
            payment["customer_id"]
        ).strip()

        payment_amount = float(
            payment["payment_amount"]
        )

        payment_reference = (
            self.normalize_reference(
                payment["order_id"]
            )
        )

        # Customer signal
        customer_mask = (
            candidates["customer_id"]
            .astype(str)
            .str.strip()
            == payment_customer
        )

        # Amount signal
        amount_mask = (
            (
                candidates["gross_amount"]
                - payment_amount
            ).abs()
            <= max(
                500.0,
                payment_amount * 0.05,
            )
        )

        # Reference signal
        reference_mask = (
            candidates["merchant_reference"]
            .astype(str)
            .apply(
                lambda value: (
                    self.reference_similarity(
                        payment_reference,
                        value,
                    )
                    >= 0.60
                )
            )
        )

        candidate_pool = candidates[
            customer_mask
            | amount_mask
            | reference_mask
        ].copy()

        # Safety fallback:
        # never return an empty pool just because
        # candidate blocking was too aggressive.
        if candidate_pool.empty:
            return candidates

        return candidate_pool

    def score_candidate(
        self,
        payment: pd.Series,
        settlement: pd.Series,
    ) -> MatchCandidate:
        """Calculate the weighted score for one candidate."""

        reference_score = (
            self.reference_similarity(
                payment["order_id"],
                settlement["merchant_reference"],
            )
        )

        amount_score = (
            self.amount_similarity(
                float(
                    payment["payment_amount"]
                ),
                float(
                    settlement["gross_amount"]
                ),
            )
        )

        customer_score = (
            self.customer_similarity(
                payment["customer_id"],
                settlement["customer_id"],
            )
        )

        date_score = (
            self.date_similarity(
                payment["payment_date"],
                settlement["settlement_date"],
            )
        )

        # Weighted matching score.
        final_score = (
            0.40 * reference_score
            + 0.30 * amount_score
            + 0.20 * customer_score
            + 0.10 * date_score
        )

        return MatchCandidate(
            settlement_id=str(
                settlement["settlement_id"]
            ),
            score=round(
                final_score,
                4,
            ),
            reference_similarity=round(
                reference_score,
                4,
            ),
            amount_similarity=round(
                amount_score,
                4,
            ),
            customer_similarity=round(
                customer_score,
                4,
            ),
            date_similarity=round(
                date_score,
                4,
            ),
        )

    def find_candidates(
        self,
        payment: pd.Series,
        top_k: int = 5,
    ) -> list[MatchCandidate]:
        """Return the highest-scoring candidates."""

        candidates = []

        candidate_pool = (
            self.generate_candidate_pool(
                payment
            )
        )

        for _, settlement in (
            candidate_pool.iterrows()
        ):
            candidate = self.score_candidate(
                payment,
                settlement,
            )

            candidates.append(
                candidate
            )

        candidates.sort(
            key=lambda candidate: candidate.score,
            reverse=True,
        )

        return candidates[:top_k]

    def match(
        self,
        payment: pd.Series,
    ) -> dict:
        """
        Determine the best settlement candidate.

        Confidence is based on the best score and the
        separation from the second-best candidate.
        """

        candidates = self.find_candidates(
            payment,
            top_k=5,
        )

        if not candidates:
            return {
                "status": "UNRESOLVED",
                "confidence": 0.0,
                "candidate": None,
                "margin": 0.0,
                "candidates": [],
            }

        best = candidates[0]

        second_score = (
            candidates[1].score
            if len(candidates) > 1
            else 0.0
        )

        margin = (
            best.score
            - second_score
        )

        # Strong independent evidence.
        amount_exact = (
            best.amount_similarity
            >= 0.9999
        )

        customer_exact = (
            best.customer_similarity
            == 1.0
        )

        reference_strong = (
            best.reference_similarity
            >= 0.85
        )

        # Conservative classification.
        if (
            best.score >= 0.95
            and margin >= 0.10
            and (
                amount_exact
                or reference_strong
            )
        ):
            status = "HIGH_CONFIDENCE"

        elif (
            best.score >= 0.80
            and margin >= 0.05
        ):
            status = "REVIEW"

        else:
            status = "UNRESOLVED"

        return {
            "status": status,
            "confidence": best.score,
            "candidate": best.settlement_id,
            "margin": round(
                margin,
                4,
            ),
            "candidates": [
                candidate.__dict__
                for candidate in candidates
            ],
        }