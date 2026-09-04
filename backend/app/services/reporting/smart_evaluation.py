from __future__ import annotations

import pandas as pd


def evaluate_smart_reconciliation(
    results: pd.DataFrame,
    ground_truth: pd.DataFrame,
) -> dict:

    merged = results.merge(
        ground_truth[
            [
                "payment_id",
                "expected_settlement_id",
                "true_status",
            ]
        ],
        on="payment_id",
        how="inner",
    )

    actual_matched = (
        merged["true_status"] == "matched"
    )

    predicted_matched = (
        merged["status"] == "MATCHED"
    )

    correct_matches = (
        actual_matched
        & predicted_matched
        & (
            merged[
                "settlement_id"
            ].astype(str)
            == merged[
                "expected_settlement_id"
            ].astype(str)
        )
    ).sum()

    predicted_match_count = (
        predicted_matched.sum()
    )

    actual_match_count = (
        actual_matched.sum()
    )

    false_matches = (
        predicted_matched
        & ~(
            merged[
                "settlement_id"
            ].astype(str)
            == merged[
                "expected_settlement_id"
            ].astype(str)
        )
    ).sum()

    precision = (
        correct_matches
        / predicted_match_count
        if predicted_match_count
        else 0.0
    )

    recall = (
        correct_matches
        / actual_match_count
        if actual_match_count
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "actual_matched_records": int(
            actual_match_count
        ),
        "predicted_matched_records": int(
            predicted_match_count
        ),
        "correct_matches": int(
            correct_matches
        ),
        "false_matches": int(
            false_matches
        ),
        "precision": round(
            precision * 100,
            2,
        ),
        "recall": round(
            recall * 100,
            2,
        ),
        "f1_score": round(
            f1 * 100,
            2,
        ),
    }