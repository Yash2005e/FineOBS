from pathlib import Path

import pandas as pd

from backend.app.services.reporting.metrics import (
    calculate_classification_metrics,
    calculate_exception_detection_metrics,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"


def main() -> None:
    results_path = (
        DATA_DIR / "reconciliation_results.csv"
    )

    ground_truth_path = (
        GROUND_TRUTH_DIR / "ground_truth.csv"
    )

    print("Loading evaluation data...")

    results = pd.read_csv(results_path)

    ground_truth = pd.read_csv(
        ground_truth_path
    )

    print(
        f"FineOBS results: {len(results)} records"
    )

    print(
        f"Ground truth:    {len(ground_truth)} records"
    )

    metrics = calculate_classification_metrics(
        results,
        ground_truth,
    )

    exception_metrics = (
        calculate_exception_detection_metrics(
            results,
            ground_truth,
        )
    )

    print("\n======================================")
    print("       FineOBS BASELINE EVALUATION")
    print("======================================")

    print(
        f"\nTotal Records : {metrics['total_records']}"
    )

    print(
        f"Accuracy      : {metrics['accuracy']}%"
    )

    print(
        f"Precision     : {metrics['precision']}%"
    )

    print(
        f"Recall        : {metrics['recall']}%"
    )

    print(
        f"F1 Score      : {metrics['f1_score']}%"
    )

    print("\nConfusion Matrix")
    print("----------------")
    print(
        f"True Positive  : {metrics['true_positive']}"
    )
    print(
        f"True Negative  : {metrics['true_negative']}"
    )
    print(
        f"False Positive : {metrics['false_positive']}"
    )
    print(
        f"False Negative : {metrics['false_negative']}"
    )

    print("\nException Detection")
    print("-------------------")

    for exception_type, data in (
        exception_metrics.items()
    ):
        print(
            f"{exception_type}: "
            f"{data['correctly_detected']}/"
            f"{data['actual']} "
            f"({data['detection_rate']}%)"
        )


if __name__ == "__main__":
    main()