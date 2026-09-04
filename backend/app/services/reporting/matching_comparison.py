from __future__ import annotations

import pandas as pd


def compare_matching_results(
    baseline: pd.DataFrame,
    intelligent: pd.DataFrame,
    ground_truth: pd.DataFrame,
) -> dict:

    merged = (
        ground_truth
        .merge(
            baseline[
                [
                    "payment_id",
                    "status",
                ]
            ],
            on="payment_id",
            how="inner",
        )
        .merge(
            intelligent[
                [
                    "payment_id",
                    "matched_settlement_id",
                    "matching_status",
                    "confidence",
                ]
            ],
            on="payment_id",
            how="left",
        )
    )

    actual_matched = (
        merged["true_status"] == "matched"
    )

    baseline_matched = (
        merged["status"] == "MATCHED"
    )

    intelligent_matched = (
        merged["matching_status"]
        == "HIGH_CONFIDENCE"
    )

    baseline_correct = (
        actual_matched
        & baseline_matched
    ).sum()

    intelligent_correct = (
        actual_matched
        & intelligent_matched
    ).sum()

    recovered = (
        actual_matched
        & ~baseline_matched
        & intelligent_matched
    ).sum()

    actual_total = int(
        actual_matched.sum()
    )

    baseline_recall = (
        baseline_correct
        / actual_total
        * 100
        if actual_total
        else 0.0
    )

    intelligent_recall = (
        intelligent_correct
        / actual_total
        * 100
        if actual_total
        else 0.0
    )

    return {
        "total_records": int(
            len(merged)
        ),
        "actual_matched_records": actual_total,
        "baseline_correct_matches": int(
            baseline_correct
        ),
        "intelligent_correct_matches": int(
            intelligent_correct
        ),
        "new_matches_recovered": int(
            recovered
        ),
        "baseline_recall": round(
            baseline_recall,
            2,
        ),
        "intelligent_recall": round(
            intelligent_recall,
            2,
        ),
        "recall_improvement": round(
            intelligent_recall
            - baseline_recall,
            2,
        ),
    }