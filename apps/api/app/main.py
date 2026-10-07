from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.prediction import (
    router as prediction_router,
)

from app.routers.recommendation import (
    router as recommendation_router,
)


app = FastAPI(
    title="FireSense API",
    version="0.1.0",
    description=(
        "Evidence-grounded reduced-gravity "
        "fire behavior intelligence and "
        "decision-support API."
    ),
)


DEV_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=DEV_CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Content-Type",
    ],
)


app.include_router(
    prediction_router
)

app.include_router(
    recommendation_router
)


@app.get(
    "/",
    tags=["System"],
)
def root():
    return {
        "name": "FireSense API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get(
    "/health",
    tags=["System"],
)
def health():
    return {
        "status": "healthy"
    }

from app.routers.evidence import router as evidence_router
app.include_router(evidence_router)
