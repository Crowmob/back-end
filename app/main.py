from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers.main_router import main_router
from app.core.settings_model import settings
from app.db.postgres_init import create_tables, disconnect_db
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await disconnect_db()


app = FastAPI(
    version="1.0",
    description="Internship project",
    lifespan=lifespan
)

app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)