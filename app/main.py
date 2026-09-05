from fastapi import FastAPI

from app.core.database import Base, engine
from app.habits import models
from app.habits.router import router as habits_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AlToque AI API",
    description="Backend central de AlToque AI",
    version="0.2.0"
)


app.include_router(habits_router)


@app.get("/")
def root():
    return {
        "application": "AlToque AI",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "service": "altoque-ai",
        "status": "ok"
    }