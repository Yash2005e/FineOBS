from pathlib import Path

import pandas as pd

from backend.app.services.reporting.smart_evaluation import (
    evaluate_smart_reconciliation,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = (
    ROOT / "data" / "ground_truth"
)


def main() -> None:

    results = pd.read_csv(
        DATA_DIR
        / "smart_reconciliation_results.csv"
    )

    ground_truth = pd.read_csv(
        GROUND_TRUTH_DIR
        / "ground_truth.csv"
    )

    metrics = evaluate_smart_reconciliation(
        results,
        ground_truth,
    )

    print()
    print(
        "======================================"
    )
    print(
        "   FINEOBS SMART EVALUATION"
    )
    print(
        "======================================"
    )

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()