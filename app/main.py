from fastapi import FastAPI

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(health_router)
    app.include_router(chat_router)

    return app

app = create_app