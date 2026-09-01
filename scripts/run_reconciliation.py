from pathlib import Path

import pandas as pd

from backend.app.services.reconciliation.engine import (
    ReconciliationEngine,
)


ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "generated"

OUTPUT_DIR = ROOT / "data" / "generated"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def main() -> None:

    print("Loading FineOBS datasets...")

    orders = pd.read_csv(
        DATA_DIR / "orders.csv"
    )

    payments = pd.read_csv(
        DATA_DIR / "payments.csv"
    )

    settlements = pd.read_csv(
        DATA_DIR / "settlements.csv"
    )

    print(f"Orders:      {len(orders)}")
    print(f"Payments:    {len(payments)}")
    print(f"Settlements: {len(settlements)}")

    engine = ReconciliationEngine(
        orders=orders,
        payments=payments,
        settlements=settlements,
    )

    print("\nRunning reconciliation...")

    results = engine.reconcile()

    output_path = (
        OUTPUT_DIR / "reconciliation_results.csv"
    )

    results.to_csv(
        output_path,
        index=False,
    )

    print("\nReconciliation completed.")
    print(f"Results saved to: {output_path}")

    print("\nStatus summary:")
    print(results["status"].value_counts())

    print("\nException summary:")
    print(
        results[
            results["status"] == "EXCEPTION"
        ]["exception_type"].value_counts()
    )


if __name__ == "__main__":
    main()