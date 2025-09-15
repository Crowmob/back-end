from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers.admin_router import admin_router
from app.routers.main_router import main_router
from app.routers.notification_router import notification_router
from app.routers.quiz_router import quiz_router
from app.routers.user_router import user_router
from app.routers.basic_auth_router import basic_auth_router
from app.routers.auth_router import auth_router
from app.routers.company_router import company_router
from app.routers.membership_router import membership_router
from app.utils.settings_model import settings
from app.websocket.endpoints import websocket_router

app = FastAPI(version="1.0", description="Internship project")

origins = [settings.REACT_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(basic_auth_router)
app.include_router(company_router)
app.include_router(membership_router)
app.include_router(admin_router)
app.include_router(quiz_router)
app.include_router(websocket_router)
app.include_router(notification_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD
    )
