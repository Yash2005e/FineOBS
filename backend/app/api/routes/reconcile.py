from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.reconciliation import (
    ReconciliationRequest,
    ReconciliationResponse,
)
from backend.app.services.reconciliation.batch_service import (
    BatchReconciliationService,
)


router = APIRouter(
    prefix="/reconcile",
    tags=["Reconciliation"],
)


@router.post(
    "",
    response_model=ReconciliationResponse,
)
def reconcile(
    request: ReconciliationRequest,
    db: Session = Depends(get_db),
):

    service = BatchReconciliationService()

    return service.run(
        db=db,
        batch_name=request.batch_name,
    )