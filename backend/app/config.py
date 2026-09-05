"""Configuración centralizada de AlToque AI mediante Pydantic BaseSettings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import json


class Settings(BaseSettings):
    """Ajustes de la aplicación cargados desde variables de entorno o archivo .env."""

    # Aplicación
    app_name: str = "AlToque AI Backend"
    app_version: str = "0.1.0"
    debug: bool = True

    # Base de datos
    database_url: str = "postgresql+asyncpg://altoque:altoque_dev@localhost:5432/altoque_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Autenticación
    secret_key: str = "change-this-to-a-secure-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Proveedor LLM
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o"
    llm_extraction_model: str = "gpt-4o"

    # WhatsApp Business API
    whatsapp_access_token: str = ""
    whatsapp_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "altoque_webhook_verify_token"
    whatsapp_webhook_verify_token: str = "altoque_webhook_verify_token"
    whatsapp_api_version: str = "v21.0"

    # Almacenamiento de archivos
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10

    # CORS
    cors_origins: str = '["http://localhost:3000","http://localhost:8080"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """Obtiene lista de orígenes CORS parseados."""
        try:
            return json.loads(self.cors_origins)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
