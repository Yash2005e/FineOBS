from pathlib import Path

import pandas as pd

from backend.app.services.reporting.matching_comparison import (
    compare_matching_results,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"


def main() -> None:
    baseline_path = (
        DATA_DIR
        / "reconciliation_results.csv"
    )

    intelligent_path = (
        DATA_DIR
        / "intelligent_reconciliation_results.csv"
    )

    ground_truth_path = (
        GROUND_TRUTH_DIR
        / "ground_truth.csv"
    )

    print("Loading comparison datasets...")

    baseline = pd.read_csv(
        baseline_path
    )

    intelligent = pd.read_csv(
        intelligent_path
    )

    ground_truth = pd.read_csv(
        ground_truth_path
    )

    metrics = compare_matching_results(
        baseline=baseline,
        intelligent=intelligent,
        ground_truth=ground_truth,
    )

    print()
    print("======================================")
    print("       FineOBS MATCHING COMPARISON")
    print("======================================")

    for key, value in metrics.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()