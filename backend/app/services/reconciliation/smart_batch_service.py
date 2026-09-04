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


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

# smart_batch_service.py
#
# FineOBS/
# ├── backend/
# │   └── app/
# │       └── services/
# │           └── reconciliation/
# │               └── smart_batch_service.py
#
# parents[4] -> FineOBS repository root

ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = ROOT / "data" / "generated"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"


class SmartBatchReconciliationService:
    """
    Orchestrates the complete FineOBS smart
    reconciliation workflow for a batch.

    Workflow:

        Load batch
            ↓
        Smart reconciliation
            ↓
        Calculate operational metrics
            ↓
        Compare against ground truth
            ↓
        Persist exception/review records
            ↓
        Write audit logs
            ↓
        Save result CSV
            ↓
        Save evaluation JSON
            ↓
        Return complete batch report
    """

    def run(
        self,
        db: Session,
        batch_name: str,
    ) -> dict:

        start_time = time.perf_counter()

        # ==================================================
        # 1. Validate required input files
        # ==================================================

        required_files = [
            DATA_DIR / "orders.csv",
            DATA_DIR / "payments.csv",
            DATA_DIR / "settlements.csv",
            GROUND_TRUTH_DIR / "ground_truth.csv",
        ]

        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Required FineOBS data file not found: "
                    f"{file_path}"
                )

        # ==================================================
        # 2. Load source datasets
        # ==================================================

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

        # ==================================================
        # 3. Basic dataset validation
        # ==================================================

        if payments.empty:
            raise ValueError(
                "Payment dataset is empty."
            )

        if orders.empty:
            raise ValueError(
                "Order dataset is empty."
            )

        if settlements.empty:
            raise ValueError(
                "Settlement dataset is empty."
            )

        if ground_truth.empty:
            raise ValueError(
                "Ground-truth dataset is empty."
            )

        # ==================================================
        # 4. Run Smart Reconciliation
        # ==================================================

        engine = SmartReconciliationEngine(
            orders=orders,
            payments=payments,
            settlements=settlements,
        )

        results = engine.reconcile()

        # ==================================================
        # 5. Calculate operational metrics
        # ==================================================

        metrics = calculate_smart_metrics(
            results
        )

        # ==================================================
        # 6. Evaluate against ground truth
        # ==================================================

        evaluation = evaluate_results(
            results=results,
            ground_truth=ground_truth,
        )

        # ==================================================
        # 7. Calculate processing performance
        # ==================================================

        elapsed = (
            time.perf_counter()
            - start_time
        )

        total_records = len(results)

        throughput = (
            total_records / elapsed
            if elapsed > 0
            else 0.0
        )

        # ==================================================
        # 8. Generate batch ID
        # ==================================================

        batch_id = (
            f"BATCH-{uuid.uuid4().hex[:8].upper()}"
        )

        # ==================================================
        # 9. Save detailed reconciliation results
        # ==================================================

        output_path = (
            DATA_DIR
            / f"{batch_id}_smart_results.csv"
        )

        results.to_csv(
            output_path,
            index=False,
        )

        # ==================================================
        # 10. Persist exceptions / review cases
        # ==================================================

        existing_payment_ids = {
            str(payment_id)
            for payment_id, in db.query(
                ExceptionRecord.payment_id
            ).all()
        }

        created = 0

        for _, row in results.iterrows():

            status = str(
                row["status"]
            )

            # Only non-final cases need the exception queue.
            if status not in {
                "EXCEPTION",
                "REVIEW",
                "UNRESOLVED",
            }:
                continue

            payment_id = str(
                row["payment_id"]
            )

            # Prevent duplicate exception records.
            if payment_id in existing_payment_ids:
                continue

            # Safely extract nullable fields.
            order_id = (
                str(row["order_id"])
                if pd.notna(
                    row["order_id"]
                )
                else None
            )

            settlement_id = (
                str(row["settlement_id"])
                if pd.notna(
                    row["settlement_id"]
                )
                else None
            )

            payment_amount = (
                float(row["payment_amount"])
                if pd.notna(
                    row["payment_amount"]
                )
                else None
            )

            settlement_amount = (
                float(row["settlement_amount"])
                if pd.notna(
                    row["settlement_amount"]
                )
                else None
            )

            difference_amount = (
                float(row["difference_amount"])
                if pd.notna(
                    row["difference_amount"]
                )
                else None
            )

            confidence = (
                float(row["confidence"])
                if pd.notna(
                    row["confidence"]
                )
                else None
            )

            explanation = (
                str(row["explanation"])
                if pd.notna(
                    row["explanation"]
                )
                else None
            )

            ai_recommendation = None

            if (
                "ai_recommendation" in results.columns
                and pd.notna(
                    row["ai_recommendation"]
                )
            ):
                ai_recommendation = str(
                    row["ai_recommendation"]
                )

            exception = ExceptionRecord(
                payment_id=payment_id,

                order_id=order_id,

                settlement_id=settlement_id,

                exception_type=str(
                    row["exception_type"]
                ),

                payment_amount=payment_amount,

                settlement_amount=settlement_amount,

                difference_amount=difference_amount,

                confidence=confidence,

                explanation=explanation,

                ai_recommendation=ai_recommendation,

                status="OPEN",
            )

            db.add(exception)

            # Flush so exception.id is available
            # for the audit record.
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
                    f"Created by FineOBS "
                    f"smart reconciliation "
                    f"batch {batch_id}."
                ),
            )

            existing_payment_ids.add(
                payment_id
            )

            created += 1

        # ==================================================
        # 11. Commit exception + audit records
        # ==================================================

        db.commit()

        # ==================================================
        # 12. Save evaluation report
        # ==================================================

        evaluation_path = (
            DATA_DIR
            / f"{batch_id}_evaluation.json"
        )

        evaluation_report = {
            "batch_id": batch_id,
            "batch_name": batch_name,

            "dataset": {
                "orders": int(
                    len(orders)
                ),
                "payments": int(
                    len(payments)
                ),
                "settlements": int(
                    len(settlements)
                ),
                "ground_truth_records": int(
                    len(ground_truth)
                ),
            },

            "operational_metrics": metrics,

            "evaluation_metrics": evaluation,

            "performance": {
                "processing_time_seconds": round(
                    elapsed,
                    4,
                ),
                "throughput_records_per_second": round(
                    throughput,
                    2,
                ),
            },

            "exceptions_created": created,
        }

        with open(
            evaluation_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                evaluation_report,
                file,
                indent=2,
                default=str,
            )

        # ==================================================
        # 13. Build API response
        # ==================================================

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