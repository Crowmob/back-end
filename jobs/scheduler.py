from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from app.services.user import get_user_service
from app.websocket.manager import get_manager

logger = logging.getLogger(__name__)


async def quiz_completion_job():
    user_service = get_user_service()
    users = await user_service.get_users_with_quizzes_to_complete()
    manager = get_manager()
    await manager.broadcast_to_users_with_quizzes_to_complete(
        users, {"message": "Time to complete quiz"}
    )


scheduler = AsyncIOScheduler()
scheduler.add_job(
    quiz_completion_job,
    trigger="cron",
    hour=0,
    minute=0,
    second=0,
)
