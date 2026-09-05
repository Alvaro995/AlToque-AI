"""Punto de entrada de la aplicación FastAPI AlToque AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestor de ciclo de vida para inicio y parada del servicio."""
    logger.info("Iniciando backend AlToque AI versión %s", settings.app_version)
    yield
    logger.info("Deteniendo backend AlToque AI")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Copiloto inteligente de prevención metabólica. "
        "API REST para ingesta clínica, motor glucémico, "
        "hábitos físicos, red de cuidado y asistente conversacional."
    ),
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Sistema"])
async def health_check():
    """Endpoint de verificación de estado y salud del sistema."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "service": settings.app_name,
    }


# --- API v1 Router ---
from app.api.v1.router import api_v1_router  # noqa: E402

app.include_router(api_v1_router, prefix="/api/v1")
