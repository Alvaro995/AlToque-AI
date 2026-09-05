"""
AlToque AI -- Pruebas de Integración de API (Happy Path y Casos de Error Crítico)

Valida el comportamiento integral de los endpoints REST:
1. Camino feliz (Happy Path): simulación glucémica, optimización de secuencia y endpoints base.
2. Casos de error crítico: accesos no autorizados (401), tokens corruptos, archivos vacíos (400)
   y accesos denegados a webhooks (403).
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestIntegrationHappyPath:
    """Validación del camino feliz (Happy Path) del sistema."""

    def test_health_check_endpoint(self):
        """Valida que el servicio responda estado saludable en /health."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["service"] == "AlToque AI Backend"

    def test_glycemic_sequence_optimization_happy_path(self):
        """Valida optimización de orden de alimentos (F-05) vía API REST."""
        payload = [
            {"name": "Arroz con choclo", "category": "carbohydrate"},
            {"name": "Mix de lechuga y pepino", "category": "fiber"},
            {"name": "Filete de trucha", "category": "protein"},
        ]
        response = client.post("/api/v1/glycemic/sequence-optimize", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert "optimized_sequence" in data
        seq = data["optimized_sequence"]
        assert len(seq) == 3
        # Primer plato debe ser fibra
        assert seq[0]["category"] == "fiber"
        assert seq[0]["name"] == "Mix de lechuga y pepino"
        # Segundo proteína
        assert seq[1]["category"] == "protein"
        # Tercero carbohidrato
        assert seq[2]["category"] == "carbohydrate"

    def test_glycemic_curve_simulation_happy_path(self):
        """Valida generación de curvas postprandiales comparativas (F-06)."""
        response = client.post(
            "/api/v1/glycemic/simulate",
            params={"baseline_glucose": 92.0, "carb_load_grams": 45.0, "buffer_score": 8.0},
        )
        assert response.status_code == 200
        data = response.json()

        assert "isolated_curve" in data
        assert "buffered_curve" in data
        assert len(data["isolated_curve"]) > 5
        assert data["peak_reduction_pct"] > 15.0
        assert data["peak_isolated_mg_dl"] > data["peak_buffered_mg_dl"]

    def test_whatsapp_webhook_verification_happy_path(self):
        """Valida desafío de suscripción con token legítimo de WhatsApp Cloud API."""
        from app.config import settings
        token = settings.whatsapp_webhook_verify_token
        challenge_str = "1122334455"

        response = client.get(
            "/api/v1/webhooks/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": token,
                "hub.challenge": challenge_str,
            },
        )
        assert response.status_code == 200
        assert response.text == challenge_str


class TestIntegrationCriticalErrors:
    """Validación de respuestas ante casos de error crítico del sistema."""

    def test_unauthorized_access_missing_token(self):
        """Error Crítico: Petición a recurso protegido sin cabecera de autorización (401)."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Se requiere cabecera de autorización Bearer" in data["detail"]

    def test_unauthorized_access_malformed_token(self):
        """Error Crítico: Petición con token JWT manipulado o corrupto (401)."""
        headers = {"Authorization": "Bearer token_falsificado_o_corrupto_invalido"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Token inválido o expirado" in data["detail"]

    def test_whatsapp_webhook_verification_failure(self):
        """Error Crítico: Intento de suscripción a webhook con token ilegítimo (403)."""
        response = client.get(
            "/api/v1/webhooks/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "token_atacante_invalido",
                "hub.challenge": "12345",
            },
        )
        assert response.status_code == 403
        assert "Verificación de token de WhatsApp fallida" in response.json()["detail"]

    def test_upload_empty_document_error(self):
        """Error Crítico: Carga de archivo clínico vacío (0 bytes) sin contenido (400)."""
        # Para simular endpoint de carga de documento
        from app.services.auth_service import create_access_token
        valid_jwt = create_access_token(data={"sub": "test_user_id", "role": "patient"})

        headers = {"Authorization": f"Bearer {valid_jwt}"}
        # Enviar archivo con bytes vacíos
        files = {"file": ("analisis_vacio.pdf", b"", "application/pdf")}
        data = {"doc_type": "clinical"}

        response = client.post("/api/v1/ingestion/upload", headers=headers, files=files, data=data)
        assert response.status_code == 400
        assert "El archivo proporcionado está vacío" in response.json()["detail"]
