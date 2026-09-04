from pathlib import Path

import pandas as pd

from backend.app.db.database import (
    SessionLocal,
)
from backend.app.models.exception import (
    ExceptionRecord,
)
from backend.app.services.reporting.audit import (
    create_audit_log,
)


ROOT = Path(__file__).resolve().parents[1]

RESULTS_PATH = (
    ROOT
    / "data"
    / "generated"
    / "reconciliation_results.csv"
)


def main() -> None:

    results = pd.read_csv(
        RESULTS_PATH
    )

    exceptions = results[
        results["status"] == "EXCEPTION"
    ].copy()

    db = SessionLocal()

    try:

        existing_payment_ids = {
            payment_id
            for payment_id, in db.query(
                ExceptionRecord.payment_id
            ).all()
        }

        created = 0

        for _, row in exceptions.iterrows():

            payment_id = str(
                row["payment_id"]
            )

            if payment_id in existing_payment_ids:
                continue

            exception = ExceptionRecord(
                payment_id=payment_id,
                order_id=str(
                    row["order_id"]
                )
                if pd.notna(row["order_id"])
                else None,
                settlement_id=str(
                    row["settlement_id"]
                )
                if pd.notna(
                    row["settlement_id"]
                )
                else None,
                exception_type=str(
                    row["exception_type"]
                ),
                payment_amount=(
                    float(
                        row["payment_amount"]
                    )
                    if pd.notna(
                        row["payment_amount"]
                    )
                    else None
                ),
                settlement_amount=(
                    float(
                        row["settlement_amount"]
                    )
                    if pd.notna(
                        row["settlement_amount"]
                    )
                    else None
                ),
                difference_amount=(
                    float(
                        row["difference_amount"]
                    )
                    if pd.notna(
                        row["difference_amount"]
                    )
                    else None
                ),
                confidence=(
                    float(
                        row["confidence"]
                    )
                    if pd.notna(
                        row["confidence"]
                    )
                    else None
                ),
                explanation=str(
                    row["explanation"]
                ),
                status="OPEN",
            )

            db.add(exception)
            db.flush()

            create_audit_log(
                db,
                entity_type="EXCEPTION",
                entity_id=str(exception.id),
                action="CREATED",
                old_status=None,
                new_status="OPEN",
                actor="SYSTEM",
                comment=(
                    "Imported from "
                    "reconciliation results."
                ),
            )

            created += 1

        db.commit()

        print(
            f"Created {created} exception records."
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()