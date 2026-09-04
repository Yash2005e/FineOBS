from __future__ import annotations

import pandas as pd


def evaluate_results(
    results: pd.DataFrame,
    ground_truth: pd.DataFrame,
) -> dict:
    """
    Compare FineOBS smart reconciliation results
    against the known benchmark ground truth.
    """

    merged = results.merge(
        ground_truth[
            [
                "payment_id",
                "expected_settlement_id",
                "true_status",
                "exception_type",
            ]
        ],
        on="payment_id",
        how="inner",
        suffixes=("_predicted", "_truth"),
    )

    total = len(merged)

    if total == 0:
        raise ValueError(
            "No records could be matched against ground truth."
        )

    actual_matched = (
        merged["true_status"] == "matched"
    )

    predicted_matched = (
        merged["status"] == "MATCHED"
    )

    # A predicted match is correct only when
    # the settlement ID is the expected one.
    correct_match = (
        actual_matched
        & predicted_matched
        & (
            merged["settlement_id"].fillna("").astype(str)
            == merged["expected_settlement_id"]
            .fillna("")
            .astype(str)
        )
    )

    # Predicted matches that are wrong.
    incorrect_match = (
        predicted_matched
        & ~correct_match
    )

    actual_match_count = int(
        actual_matched.sum()
    )

    predicted_match_count = int(
        predicted_matched.sum()
    )

    correct_match_count = int(
        correct_match.sum()
    )

    incorrect_match_count = int(
        incorrect_match.sum()
    )

    precision = (
        correct_match_count / predicted_match_count
        if predicted_match_count
        else 0.0
    )

    recall = (
        correct_match_count / actual_match_count
        if actual_match_count
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    # Category-level exception detection.
    actual_exceptions = merged[
        merged["exception_type_truth"] != "none"
    ]

    exception_detection = {}

    for exception_type in sorted(
        actual_exceptions[
            "exception_type_truth"
        ].unique()
    ):
        actual = (
            merged["exception_type_truth"]
            == exception_type
        )

        predicted = (
            merged["exception_type_predicted"]
            == exception_type
        )

        correctly_detected = int(
            (actual & predicted).sum()
        )

        actual_count = int(
            actual.sum()
        )

        detection_rate = (
            correctly_detected / actual_count * 100
            if actual_count
            else 0.0
        )

        exception_detection[
            exception_type
        ] = {
            "actual": actual_count,
            "correctly_detected": correctly_detected,
            "detection_rate": round(
                detection_rate,
                2,
            ),
        }

    # Overall match rate from the produced result.
    match_rate = (
        predicted_match_count / total * 100
    )

    review_count = int(
        (
            merged["status"]
            == "REVIEW"
        ).sum()
    )

    unresolved_count = int(
        (
            merged["status"]
            == "UNRESOLVED"
        ).sum()
    )

    exception_count = int(
        (
            merged["status"]
            == "EXCEPTION"
        ).sum()
    )

    return {
        "total_records": total,

        "matched_records": predicted_match_count,
        "exception_records": exception_count,
        "review_records": review_count,
        "unresolved_records": unresolved_count,

        "match_rate": round(
            match_rate,
            2,
        ),

        "exception_rate": round(
            exception_count / total * 100,
            2,
        ),

        "review_rate": round(
            review_count / total * 100,
            2,
        ),

        "unresolved_rate": round(
            unresolved_count / total * 100,
            2,
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

        "correctly_reconciled": (
            correct_match_count
        ),

        "incorrect_reconciliations": (
            incorrect_match_count
        ),

        "exception_detection": (
            exception_detection
        ),
    }