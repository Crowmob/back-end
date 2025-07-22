import logging

from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.core.settings_model import settings
from app.core.exceptions.auth_exceptions import UnauthorizedException

logger = logging.getLogger(__name__)


def create_access_token(id: int):
    data = {"id": id}
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.EXP_TIME)
    to_encode.update({"exp": int(expire.timestamp())})
    logger.info("Created access token")
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str):
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return data
    except JWTError:
        logger.error("Invalid token")
        raise UnauthorizedException(detail="Invalid token")
