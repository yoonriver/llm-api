from fastapi import FastAPI

from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_history import router as history_router
from app.api.routes_storage import router as storage_router
from app.core.config import settings
from app.api.routes_chain import router as chain_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(storage_router)
    app.include_router(history_router)
    app.include_router(chain_router)

    return app


app = create_app()