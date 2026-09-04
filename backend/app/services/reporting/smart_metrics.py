from __future__ import annotations

import pandas as pd


def calculate_smart_metrics(
    results: pd.DataFrame,
) -> dict:

    total = len(results)

    if total == 0:
        return {
            "total_records": 0,
            "matched_records": 0,
            "exception_records": 0,
            "review_records": 0,
            "unresolved_records": 0,
            "match_rate": 0.0,
            "review_rate": 0.0,
            "unresolved_rate": 0.0,
            "exception_rate": 0.0,
        }

    matched = int(
        (
            results["status"]
            == "MATCHED"
        ).sum()
    )

    exceptions = int(
        (
            results["status"]
            == "EXCEPTION"
        ).sum()
    )

    review = int(
        (
            results["status"]
            == "REVIEW"
        ).sum()
    )

    unresolved = int(
        (
            results["status"]
            == "UNRESOLVED"
        ).sum()
    )

    decision_source = (
        results[
            "decision_source"
        ]
        .value_counts()
        .to_dict()
    )

    exception_distribution = (
        results[
            results["exception_type"] != "none"
        ]["exception_type"]
        .value_counts()
        .to_dict()
    )

    return {
        "total_records": total,

        "matched_records": matched,

        "exception_records": exceptions,

        "review_records": review,

        "unresolved_records": unresolved,

        "match_rate": round(
            matched / total * 100,
            2,
        ),

        "review_rate": round(
            review / total * 100,
            2,
        ),

        "unresolved_rate": round(
            unresolved / total * 100,
            2,
        ),

        "exception_rate": round(
            exceptions / total * 100,
            2,
        ),

        "decision_source": {
            str(key): int(value)
            for key, value in decision_source.items()
        },

        "exception_distribution": {
            str(key): int(value)
            for key, value in exception_distribution.items()
        },
    }