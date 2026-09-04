from pathlib import Path

import pandas as pd

from backend.app.services.reconciliation.intelligent_engine import (
    IntelligentReconciliationEngine,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"


def main() -> None:

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    settlements = pd.read_csv(
        DATA_DIR / "settlements.csv"
    )

    engine = IntelligentReconciliationEngine(
        payments,
        settlements,
    )

    print(
        "Running intelligent reconciliation..."
    )

    results = engine.reconcile()

    output = (
        DATA_DIR
        / "intelligent_reconciliation_results.csv"
    )

    results.to_csv(
        output,
        index=False,
    )

    print(
        f"\nSaved to: {output}"
    )

    print(
        "\nMatching status:"
    )

    print(
        results[
            "matching_status"
        ].value_counts()
    )

    print(
        "\nConfidence statistics:"
    )

    print(
        results[
            "confidence"
        ].describe()
    )


if __name__ == "__main__":
    main()