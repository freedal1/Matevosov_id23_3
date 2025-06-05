from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.core.websocket import manager
from app.api.deps import get_current_user
from app.models.user import User
from app.cruds.task import get_task
from app.db.session import get_db
from sqlalchemy.orm import Session
import asyncio

router = APIRouter()

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверяем существование задачи и принадлежность её пользователю
    task = get_task(db, task_id)
    if not task or task.user_id != current_user.id:
        await websocket.close(code=4004, reason="Task not found or access denied")
        return

    await manager.connect(websocket, current_user.id, task_id)
    try:
        while True:
            # Keep the connection alive and wait for client messages
            data = await websocket.receive_text()
            # You can handle client messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, current_user.id, task_id) 