from fastapi import FastAPI
from .routers.main_router import main_router
from .schemas.settings_model import settings

app = FastAPI(
    version="1.0",
    description="Internship project"
)
# Adding router
app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)