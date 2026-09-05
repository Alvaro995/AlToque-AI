from fastapi import FastAPI

from app.core.database import Base, engine


# Importación de modelos para creación de tablas
from app.habits import models as habits_models
from app.users import models as users_models
from app.profiles import models as profiles_models


# Importación de routers
from app.habits.router import router as habits_router
from app.users.router import router as users_router
from app.profiles.router import router as profiles_router
from app.risk.router import router as risk_router
from app.chatbot.router import router as chatbot_router

# Crear tablas en PostgreSQL
Base.metadata.create_all(bind=engine)


app = FastAPI(

    title="AlToque AI API",

    description="Backend central de AlToque AI",

    version="0.3.0"

)


# Registrar módulos API

app.include_router(habits_router)

app.include_router(users_router)

app.include_router(profiles_router)

app.include_router(risk_router)

app.include_router(chatbot_router)

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