from typing import Any

from pydantic import BaseModel


class ReconciliationRequest(BaseModel):
    batch_name: str = "default_batch"


class ReconciliationResponse(BaseModel):
    batch_id: str
    batch_name: str

    total_records: int

    matched_records: int
    exception_records: int
    review_records: int
    unresolved_records: int

    match_rate: float
    exception_rate: float
    review_rate: float
    unresolved_rate: float

    precision: float
    recall: float
    f1_score: float

    correctly_reconciled: int
    incorrect_reconciliations: int

    decision_source: dict[str, int]

    exception_distribution: dict[str, int]

    processing_time_seconds: float
    throughput_records_per_second: float

    new_exceptions_created: int

    results_file: str