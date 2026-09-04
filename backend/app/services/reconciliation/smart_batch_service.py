from __future__ import annotations

import json
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
from backend.app.services.reporting.integrated_evaluation import (
    evaluate_results,
)
from backend.app.services.reporting.smart_metrics import (
    calculate_smart_metrics,
)


ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"


class SmartBatchReconciliationService:

    def run(
        self,
        db: Session,
        batch_name: str,
    ) -> dict:

        start_time = time.perf_counter()

        # ---------------------------------------------
        # 1. Load benchmark data
        # ---------------------------------------------

        orders = pd.read_csv(
            DATA_DIR / "orders.csv"
        )

        payments = pd.read_csv(
            DATA_DIR / "payments.csv"
        )

        settlements = pd.read_csv(
            DATA_DIR / "settlements.csv"
        )

        ground_truth = pd.read_csv(
            GROUND_TRUTH_DIR / "ground_truth.csv"
        )

        # ---------------------------------------------
        # 2. Run smart reconciliation
        # ---------------------------------------------

        engine = SmartReconciliationEngine(
            orders=orders,
            payments=payments,
            settlements=settlements,
        )

        results = engine.reconcile()

        # ---------------------------------------------
        # 3. Operational metrics
        # ---------------------------------------------

        metrics = calculate_smart_metrics(
            results
        )

        # ---------------------------------------------
        # 4. Ground-truth evaluation
        # ---------------------------------------------

        evaluation = evaluate_results(
            results=results,
            ground_truth=ground_truth,
        )

        # ---------------------------------------------
        # 5. Performance
        # ---------------------------------------------

        elapsed = (
            time.perf_counter()
            - start_time
        )

        throughput = (
            len(results) / elapsed
            if elapsed > 0
            else 0.0
        )

        # ---------------------------------------------
        # 6. Batch ID
        # ---------------------------------------------

        batch_id = (
            f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        )

        # ---------------------------------------------
        # 7. Save detailed results
        # ---------------------------------------------

        output_path = (
            DATA_DIR
            / f"{batch_id}_smart_results.csv"
        )

        results.to_csv(
            output_path,
            index=False,
        )

        # ---------------------------------------------
        # 8. Persist exception/review cases
        # ---------------------------------------------

        existing_payment_ids = {
            payment_id
            for payment_id, in db.query(
                ExceptionRecord.payment_id
            ).all()
        }

        created = 0

        for _, row in results.iterrows():

            status = str(
                row["status"]
            )

            if status not in {
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
                    float(row["settlement_amount"])
                    if pd.notna(
                        row["settlement_amount"]
                    )
                    else None
                ),
                difference_amount=(
                    float(row["difference_amount"])
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
                entity_id=str(
                    exception.id
                ),
                action="CREATED",
                old_status=None,
                new_status="OPEN",
                actor="SYSTEM",
                comment=(
                    f"Created during smart "
                    f"batch {batch_id}."
                ),
            )

            existing_payment_ids.add(
                payment_id
            )

            created += 1

        db.commit()

        # ---------------------------------------------
        # 9. Save evaluation report
        # ---------------------------------------------

        evaluation_path = (
            DATA_DIR
            / f"{batch_id}_evaluation.json"
        )

        with open(
            evaluation_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                {
                    "batch_id": batch_id,
                    "batch_name": batch_name,
                    **evaluation,
                },
                file,
                indent=2,
            )

        # ---------------------------------------------
        # 10. Final response
        # ---------------------------------------------

        return {
            "batch_id": batch_id,
            "batch_name": batch_name,

            "total_records": metrics[
                "total_records"
            ],

            "matched_records": metrics[
                "matched_records"
            ],

            "exception_records": metrics[
                "exception_records"
            ],

            "review_records": metrics[
                "review_records"
            ],

            "unresolved_records": metrics[
                "unresolved_records"
            ],

            "match_rate": metrics[
                "match_rate"
            ],

            "exception_rate": metrics[
                "exception_rate"
            ],

            "review_rate": metrics[
                "review_rate"
            ],

            "unresolved_rate": metrics[
                "unresolved_rate"
            ],

            "precision": evaluation[
                "precision"
            ],

            "recall": evaluation[
                "recall"
            ],

            "f1_score": evaluation[
                "f1_score"
            ],

            "correctly_reconciled": evaluation[
                "correctly_reconciled"
            ],

            "incorrect_reconciliations": evaluation[
                "incorrect_reconciliations"
            ],

            "decision_source": metrics[
                "decision_source"
            ],

            "exception_distribution": metrics[
                "exception_distribution"
            ],

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

            "evaluation_file": str(
                evaluation_path
            ),
        }