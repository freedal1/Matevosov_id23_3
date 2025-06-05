from fastapi import WebSocket
from typing import Dict, List, Set
import json
from app.schemas.task import WebSocketMessage

class ConnectionManager:
    def __init__(self):
        # user_id -> Dict[task_id -> List[WebSocket]]
        self.active_connections: Dict[int, Dict[str, List[WebSocket]]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, task_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        if task_id not in self.active_connections[user_id]:
            self.active_connections[user_id][task_id] = []
        self.active_connections[user_id][task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int, task_id: str):
        if user_id in self.active_connections and task_id in self.active_connections[user_id]:
            self.active_connections[user_id][task_id].remove(websocket)
            if not self.active_connections[user_id][task_id]:
                del self.active_connections[user_id][task_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_task_update(self, user_id: int, task_id: str, message):
        if user_id in self.active_connections and task_id in self.active_connections[user_id]:
            for connection in self.active_connections[user_id][task_id]:
                try:
                    if hasattr(message, 'dict'):
                        await connection.send_json(message.dict())
                    else:
                        await connection.send_json(message)
                except Exception:
                    # Handle connection errors
                    pass

    def get_active_tasks(self, user_id: int) -> Set[str]:
        """Получить список активных задач пользователя"""
        if user_id in self.active_connections:
            return set(self.active_connections[user_id].keys())
        return set()

manager = ConnectionManager() 