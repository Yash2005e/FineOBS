from pathlib import Path

import pandas as pd

from backend.app.services.reconciliation.smart_engine import (
    SmartReconciliationEngine,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"


def main() -> None:

    orders = pd.read_csv(
        DATA_DIR / "orders.csv"
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    settlements = pd.read_csv(
        DATA_DIR / "settlements.csv"
    )

    engine = SmartReconciliationEngine(
        orders=orders,
        payments=payments,
        settlements=settlements,
    )

    print(
        "Running FineOBS Smart Reconciliation..."
    )

    results = engine.reconcile()

    output_path = (
        DATA_DIR
        / "smart_reconciliation_results.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    print()
    print(
        "Results saved to:"
    )
    print(output_path)

    print()
    print("Status:")
    print(
        results["status"].value_counts()
    )

    print()
    print("Decision source:")
    print(
        results[
            "decision_source"
        ].value_counts()
    )

    print()
    print("Exception types:")
    print(
        results[
            "exception_type"
        ].value_counts()
    )


if __name__ == "__main__":
    main()