from __future__ import annotations

import pandas as pd


def calculate_classification_metrics(
    results: pd.DataFrame,
    ground_truth: pd.DataFrame,
) -> dict:
    """
    Compare FineOBS reconciliation decisions against
    the known ground truth.
    """

    merged = results.merge(
        ground_truth[
            [
                "payment_id",
                "true_status",
                "exception_type",
            ]
        ],
        on="payment_id",
        how="inner",
    )

    if merged.empty:
        raise ValueError(
            "No matching payment IDs found between "
            "results and ground truth."
        )

    # FineOBS classification
    predicted_exception = (
        merged["status"] == "EXCEPTION"
    )

    # Ground-truth classification
    actual_exception = (
        merged["true_status"] == "exception"
    )

    true_positive = (
        predicted_exception & actual_exception
    ).sum()

    true_negative = (
        ~predicted_exception & ~actual_exception
    ).sum()

    false_positive = (
        predicted_exception & ~actual_exception
    ).sum()

    false_negative = (
        ~predicted_exception & actual_exception
    ).sum()

    total = len(merged)

    accuracy = (
        (true_positive + true_negative) / total
        if total
        else 0.0
    )

    precision = (
        true_positive
        / (true_positive + false_positive)
        if (true_positive + false_positive)
        else 0.0
    )

    recall = (
        true_positive
        / (true_positive + false_negative)
        if (true_positive + false_negative)
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return {
        "total_records": int(total),
        "true_positive": int(true_positive),
        "true_negative": int(true_negative),
        "false_positive": int(false_positive),
        "false_negative": int(false_negative),
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2),
    }


def calculate_exception_detection_metrics(
    results: pd.DataFrame,
    ground_truth: pd.DataFrame,
) -> dict:
    """
    Evaluate whether FineOBS correctly identified
    specific exception categories.
    """

    merged = results.merge(
        ground_truth[
            [
                "payment_id",
                "exception_type",
            ]
        ],
        on="payment_id",
        how="inner",
        suffixes=("_predicted", "_true"),
    )

    # Ignore clean transactions for category analysis.
    actual_exceptions = merged[
        merged["exception_type_true"] != "none"
    ]

    if actual_exceptions.empty:
        return {}

    category_results = {}

    for exception_type in sorted(
        actual_exceptions["exception_type_true"].unique()
    ):
        actual = (
            merged["exception_type_true"]
            == exception_type
        )

        predicted = (
            merged["exception_type_predicted"]
            == exception_type
        )

        correct = (actual & predicted).sum()

        total_actual = actual.sum()

        detection_rate = (
            correct / total_actual
            if total_actual
            else 0.0
        )

        category_results[exception_type] = {
            "actual": int(total_actual),
            "correctly_detected": int(correct),
            "detection_rate": round(
                detection_rate * 100,
                2,
            ),
        }

    return category_results