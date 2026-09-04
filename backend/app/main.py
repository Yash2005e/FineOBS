from fastapi import FastAPI

from backend.app.api.routes.audit import (
    router as audit_router,
)
from backend.app.api.routes.exceptions import (
    router as exceptions_router,
)
from backend.app.api.routes.reconcile import (
    router as reconcile_router,
)
from backend.app.api.routes.smart_reconcile import (
    router as smart_reconcile_router,
)
from backend.app.api.routes.summary import (
    router as summary_router,
)


app = FastAPI(
    title="FineOBS API",
    description=(
        "AI Finance Controller for "
        "financial operations and reconciliation"
    ),
    version="0.4.0",
)


app.include_router(reconcile_router)
app.include_router(smart_reconcile_router)
app.include_router(exceptions_router)
app.include_router(audit_router)
app.include_router(summary_router)


@app.get("/")
def root():
    return {
        "project": "FineOBS",
        "description": "AI Finance Controller",
        "status": "running",
        "version": "0.4.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}