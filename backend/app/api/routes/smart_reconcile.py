from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.reconciliation import (
    ReconciliationRequest,
    ReconciliationResponse,
)
from backend.app.services.reconciliation.smart_batch_service import (
    SmartBatchReconciliationService,
)


router = APIRouter(
    prefix="/reconcile",
    tags=["Reconciliation"],
)


@router.post(
    "/smart",
    response_model=ReconciliationResponse,
)
def smart_reconcile(
    request: ReconciliationRequest,
    db: Session = Depends(get_db),
):

    service = SmartBatchReconciliationService()

    return service.run(
        db=db,
        batch_name=request.batch_name,
    )