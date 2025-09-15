import asyncio

from fastapi import APIRouter, WebSocket, Depends
from starlette.websockets import WebSocketDisconnect

from app.websocket.manager import get_manager, ConnectionManager

websocket_router = APIRouter(tags=["Websocket"], prefix="/ws")


@websocket_router.websocket("/notifications/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    manager: ConnectionManager = Depends(get_manager),
):
    await manager.connect(user_id, websocket)
    try:
        while True:
            await asyncio.sleep(3600)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
