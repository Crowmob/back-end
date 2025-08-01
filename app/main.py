from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.main_router import main_router
from app.routers.user_router import user_router
from app.routers.basic_auth_router import basic_auth_router
from app.routers.auth_router import auth_router
from app.routers.compony_router import company_router
from app.utils.settings_model import settings

app = FastAPI(version="1.0", description="Internship project")

origins = [settings.REACT_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(basic_auth_router)
app.include_router(company_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
