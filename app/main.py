from fastapi import FastAPI

from app.routers.main_router import main_router
from app.core.settings_model import settings

app = FastAPI(
    version="1.0",
    description="Internship project"
)

app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)