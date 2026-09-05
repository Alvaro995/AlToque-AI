"""Enrutador maestro que consolida los módulos de la API v1."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.scheduling import router as scheduling_router
from app.api.v1.glycemic import router as glycemic_router
from app.api.v1.physical import router as physical_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.care_network import router as care_network_router
from app.api.v1.chat import router as chat_router
from app.api.v1.risk import router as risk_router
from app.api.v1.reports import router as reports_router
from app.api.v1.webhooks import router as webhooks_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(ingestion_router)
api_v1_router.include_router(scheduling_router)
api_v1_router.include_router(glycemic_router)
api_v1_router.include_router(physical_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(care_network_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(risk_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(webhooks_router)
