from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.tasks import router as tasks_router
from app.core.config import settings
from app.db.seed import seed_default_measures
from app.db.session import SessionLocal

app = FastAPI(title="HEDIS AI Review API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)


@app.on_event("startup")
def seed_reference_data() -> None:
    session = SessionLocal()
    try:
        seed_default_measures(session)
    finally:
        session.close()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
