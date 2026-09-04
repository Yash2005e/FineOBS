from pathlib import Path

import pandas as pd

from backend.app.services.reconciliation.smart_engine import (
    SmartReconciliationEngine,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"


def main() -> None:

    print()
    print("=" * 60)
    print("             FINEOBS FINAL PIPELINE TEST")
    print("=" * 60)

    required_files = [
        DATA_DIR / "orders.csv",
        DATA_DIR / "payments.csv",
        DATA_DIR / "settlements.csv",
    ]

    print("\nChecking input files...")

    for path in required_files:

        if not path.exists():
            raise FileNotFoundError(
                f"Missing required file: {path}"
            )

        print(f"  OK: {path.name}")

    print("\nLoading data...")

    orders = pd.read_csv(
        DATA_DIR / "orders.csv"
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    settlements = pd.read_csv(
        DATA_DIR / "settlements.csv"
    )

    print(
        f"  Orders:      {len(orders)}"
    )

    print(
        f"  Payments:    {len(payments)}"
    )

    print(
        f"  Settlements: {len(settlements)}"
    )

    print("\nRunning smart reconciliation...")

    engine = SmartReconciliationEngine(
        orders=orders,
        payments=payments,
        settlements=settlements,
    )

    results = engine.reconcile()

    print(
        f"  Processed: {len(results)} records"
    )

    print("\nStatus distribution:")

    print(
        results["status"]
        .value_counts()
        .to_string()
    )

    print("\nDecision sources:")

    print(
        results["decision_source"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nException distribution:")

    exceptions = results[
        results["exception_type"] != "none"
    ]

    if exceptions.empty:
        print("  No exceptions.")
    else:
        print(
            exceptions[
                "exception_type"
            ]
            .value_counts()
            .to_string()
        )

    output_path = (
        DATA_DIR
        / "final_pipeline_results.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nSaved results to:\n{output_path}"
    )

    print()
    print("=" * 60)
    print("             PIPELINE TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()