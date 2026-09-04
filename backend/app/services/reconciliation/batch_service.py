from __future__ import annotations

import time
import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.exception import ExceptionRecord
from backend.app.services.reconciliation.engine import (
    ReconciliationEngine,
)
from backend.app.services.reporting.audit import (
    create_audit_log,
)


# batch_service.py
# FineOBS/
#   backend/
#       app/
#           services/
#               reconciliation/
#
# parents[4] -> repository root
ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = ROOT / "data" / "generated"


class BatchReconciliationService:

    def run(
        self,
        db: Session,
        batch_name: str,
    ) -> dict:

        start_time = time.perf_counter()

        # --------------------------------------------------
        # 1. Load source data
        # --------------------------------------------------

        orders = pd.read_csv(
            DATA_DIR / "orders.csv"
        )

        payments = pd.read_csv(
            DATA_DIR / "payments.csv"
        )

        settlements = pd.read_csv(
            DATA_DIR / "settlements.csv"
        )

        # --------------------------------------------------
        # 2. Run reconciliation
        # --------------------------------------------------

        engine = ReconciliationEngine(
            orders=orders,
            payments=payments,
            settlements=settlements,
        )

        results = engine.reconcile()

        # --------------------------------------------------
        # 3. Calculate metrics
        # --------------------------------------------------

        total = len(results)

        matched = int(
            (
                results["status"] == "MATCHED"
            ).sum()
        )

        exceptions = int(
            (
                results["status"] == "EXCEPTION"
            ).sum()
        )

        unresolved = int(
            (
                results["status"] == "UNRESOLVED"
            ).sum()
        )

        match_rate = (
            matched / total * 100
            if total
            else 0.0
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        throughput = (
            total / elapsed
            if elapsed > 0
            else 0.0
        )

        batch_id = (
            f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        )

        # --------------------------------------------------
        # 4. Save batch result
        # --------------------------------------------------

        output_path = (
            DATA_DIR
            / f"{batch_id}_results.csv"
        )

        results.to_csv(
            output_path,
            index=False,
        )

        # --------------------------------------------------
        # 5. Persist new exceptions
        # --------------------------------------------------

        existing_payment_ids = {
            payment_id
            for payment_id, in db.query(
                ExceptionRecord.payment_id
            ).all()
        }

        new_exception_count = 0

        for _, row in results.iterrows():

            if row["status"] != "EXCEPTION":
                continue

            payment_id = str(
                row["payment_id"]
            )

            # Prevent duplicate exceptions if the
            # same benchmark is reconciled repeatedly.
            if payment_id in existing_payment_ids:
                continue

            exception = ExceptionRecord(
                payment_id=payment_id,
                order_id=(
                    str(row["order_id"])
                    if pd.notna(row["order_id"])
                    else None
                ),
                settlement_id=(
                    str(row["settlement_id"])
                    if pd.notna(
                        row["settlement_id"]
                    )
                    else None
                ),
                exception_type=str(
                    row["exception_type"]
                ),
                payment_amount=(
                    float(row["payment_amount"])
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
                    float(row["confidence"])
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
                    f"Created during batch "
                    f"{batch_id}."
                ),
            )

            existing_payment_ids.add(
                payment_id
            )

            new_exception_count += 1

        db.commit()

        return {
            "batch_id": batch_id,
            "batch_name": batch_name,

            "total_records": total,
            "matched_records": matched,
            "exception_records": exceptions,
            "unresolved_records": unresolved,

            "match_rate": round(
                match_rate,
                2,
            ),

            "processing_time_seconds": round(
                elapsed,
                4,
            ),

            "throughput_records_per_second": round(
                throughput,
                2,
            ),

            "new_exceptions_created": (
                new_exception_count
            ),

            "results_file": str(
                output_path
            ),
        }