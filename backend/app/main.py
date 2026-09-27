from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.reports import router as reports_router
from app.api.triage import router as triage_router

app = FastAPI(title="DevLens API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(reports_router)
app.include_router(triage_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
