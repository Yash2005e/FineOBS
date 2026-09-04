from __future__ import annotations

import time
import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models.exception import ExceptionRecord
from backend.app.services.reconciliation.smart_engine import (
    SmartReconciliationEngine,
)
from backend.app.services.reporting.audit import (
    create_audit_log,
)
from backend.app.services.reporting.smart_metrics import (
    calculate_smart_metrics,
)


ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = ROOT / "data" / "generated"


class SmartBatchReconciliationService:

    def run(
        self,
        db: Session,
        batch_name: str,
    ) -> dict:

        start_time = time.perf_counter()

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

        results = engine.reconcile()

        metrics = calculate_smart_metrics(
            results
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        throughput = (
            len(results) / elapsed
            if elapsed > 0
            else 0.0
        )

        batch_id = (
            f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        )

        output_path = (
            DATA_DIR
            / f"{batch_id}_smart_results.csv"
        )

        results.to_csv(
            output_path,
            index=False,
        )

        # --------------------------------------------------
        # Persist exceptions and review cases
        # --------------------------------------------------

        existing_payment_ids = {
            payment_id
            for payment_id, in db.query(
                ExceptionRecord.payment_id
            ).all()
        }

        created = 0

        for _, row in results.iterrows():

            if row["status"] not in {
                "EXCEPTION",
                "REVIEW",
                "UNRESOLVED",
            }:
                continue

            payment_id = str(
                row["payment_id"]
            )

            if payment_id in existing_payment_ids:
                continue

            exception = ExceptionRecord(
                payment_id=payment_id,
                order_id=(
                    str(row["order_id"])
                    if pd.notna(
                        row["order_id"]
                    )
                    else None
                ),
                settlement_id=(
                    str(
                        row["settlement_id"]
                    )
                    if pd.notna(
                        row["settlement_id"]
                    )
                    else None
                ),
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
                entity_id=str(
                    exception.id
                ),
                action="CREATED",
                old_status=None,
                new_status="OPEN",
                actor="SYSTEM",
                comment=(
                    f"Created by smart "
                    f"reconciliation batch "
                    f"{batch_id}."
                ),
            )

            existing_payment_ids.add(
                payment_id
            )

            created += 1

        db.commit()

        return {
            "batch_id": batch_id,
            "batch_name": batch_name,

            **metrics,

            "processing_time_seconds": round(
                elapsed,
                4,
            ),

            "throughput_records_per_second": round(
                throughput,
                2,
            ),

            "new_exceptions_created": created,

            "results_file": str(
                output_path
            ),
        }