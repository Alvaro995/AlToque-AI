# Diagrama de Despliegue -- AlToque AI

## Arquitectura de Despliegue Local (Docker Compose)

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "altoque_api"
            FASTAPI["FastAPI Application"]
            UVICORN["Uvicorn ASGI Server"]
            ALEMBIC["Alembic Migrations"]
        end

        subgraph "altoque_db"
            PG["PostgreSQL 16"]
            PGVEC["pgvector Extension"]
        end

        subgraph "altoque_redis"
            RED["Redis 7 Alpine"]
        end

        subgraph "Volumes"
            PGDATA["pgdata"]
            REDDATA["redisdata"]
            UPLOADS["uploads"]
        end
    end

    subgraph "External Services"
        LLM_API["LLM Provider API"]
        WA_API["WhatsApp Business Cloud API"]
    end

    subgraph "Clients"
        MOBILE["Flutter App"]
        WHATSAPP["WhatsApp Client"]
    end

    MOBILE --> FASTAPI
    WHATSAPP --> WA_API --> FASTAPI
    FASTAPI --> PG
    FASTAPI --> RED
    FASTAPI --> LLM_API
    FASTAPI --> WA_API

    PG --> PGDATA
    RED --> REDDATA
    FASTAPI --> UPLOADS

    UVICORN --> FASTAPI
    ALEMBIC --> PG
    PGVEC --> PG
```

## Servicios Docker Compose

| Servicio | Imagen | Puerto | Healthcheck |
|----------|--------|--------|-------------|
| db | pgvector/pgvector:pg16 | 5432 | pg_isready |
| redis | redis:7-alpine | 6379 | redis-cli ping |
| api | Build desde backend/Dockerfile | 8000 | HTTP /health |

## Variables de Entorno Requeridas

| Variable | Servicio | Descripcion |
|----------|----------|-------------|
| DATABASE_URL | api | Connection string PostgreSQL (asyncpg) |
| REDIS_URL | api | Connection string Redis |
| SECRET_KEY | api | Clave para firma de JWT |
| LLM_PROVIDER | api | Proveedor LLM (openai, gemini, anthropic) |
| LLM_API_KEY | api | API key del proveedor LLM |
| LLM_MODEL | api | Modelo LLM a utilizar |
| WHATSAPP_ACCESS_TOKEN | api | Token de WhatsApp Business API |
| WHATSAPP_PHONE_NUMBER_ID | api | ID del numero de WhatsApp |
| WHATSAPP_VERIFY_TOKEN | api | Token de verificacion del webhook |
| POSTGRES_USER | db | Usuario de PostgreSQL |
| POSTGRES_PASSWORD | db | Contrasena de PostgreSQL |
| POSTGRES_DB | db | Nombre de la base de datos |

## Flujo de Inicializacion

```mermaid
sequenceDiagram
    participant DC as Docker Compose
    participant DB as PostgreSQL
    participant RD as Redis
    participant API as FastAPI

    DC->>DB: Iniciar contenedor
    DC->>RD: Iniciar contenedor
    DB-->>DC: Healthcheck OK
    RD-->>DC: Healthcheck OK
    DC->>API: Iniciar contenedor (depends_on healthy)
    API->>DB: Ejecutar migraciones Alembic
    DB-->>API: Migraciones aplicadas
    API->>DB: Verificar extension pgvector
    API->>RD: Verificar conexion Redis
    API-->>DC: Servidor ASGI escuchando en puerto 8000
```

## Consideraciones de Produccion

Para un despliegue en produccion se requiere:

1. **Reverse proxy**: Nginx o Traefik delante de Uvicorn para terminacion SSL.
2. **Workers**: Configurar multiples workers de Uvicorn (2 * CPU cores + 1).
3. **Backups**: Backup automatizado de PostgreSQL (pg_dump o WAL archiving).
4. **Secrets management**: Vault, AWS Secrets Manager o equivalente en lugar de archivo .env.
5. **Logging**: Salida estructurada JSON hacia un agregador (ELK, CloudWatch, Datadog).
6. **Monitoring**: Metricas de Prometheus + Grafana para latencia, errores y uso de recursos.
7. **CI/CD**: Pipeline de build, test y deploy automatizado.
