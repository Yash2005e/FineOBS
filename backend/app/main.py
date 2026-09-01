from fastapi import FastAPI

app = FastAPI(
    title="FineOBS API",
    description="AI Finance Controller for financial operations and reconciliation",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": "FineOBS",
        "description": "AI Finance Controller",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }