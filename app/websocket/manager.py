from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.schemas.user import UserDetailResponse
from app.services.membership import get_membership_service


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    @staticmethod
    async def send_personal_message(websocket: WebSocket, message: dict):
        await websocket.send_json(message)

    async def broadcast_to_company(self, company_id: int, message: dict):
        membership_services = get_membership_service()
        users = await membership_services.get_users_in_company(company_id)
        for user in users.items:
            if user.id in self.active_connections.keys():
                dead_connections = []
                for connection in self.active_connections[user.id]:
                    try:
                        await connection.send_json(message)
                    except WebSocketDisconnect:
                        dead_connections.append(connection)
                for dead_connection in dead_connections:
                    self.disconnect(user.id, dead_connection)

    async def broadcast_to_users_with_quizzes_to_complete(
        self, users: list[UserDetailResponse], message: dict
    ):
        for user in users:
            if user.id in self.active_connections.keys():
                dead_connections = []
                for connection in self.active_connections[user.id]:
                    try:
                        await connection.send_json(message)
                    except WebSocketDisconnect:
                        dead_connections.append(connection)
                for dead_connection in dead_connections:
                    self.disconnect(user.id, dead_connection)


manager = ConnectionManager()


def get_manager() -> ConnectionManager:
    return manager
