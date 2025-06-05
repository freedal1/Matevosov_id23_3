from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    task_id: str
    operation: str
    status: str
    progress: Optional[int] = 0
    result: Optional[Dict[str, Any]] = None

class TaskCreate(TaskBase):
    user_id: int

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WebSocketMessage(BaseModel):
    status: str
    task_id: str
    operation: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None

# Новые схемы для входящих данных запросов
class EncodeRequestPayload(BaseModel):
    text: str
    key: str

class DecodeRequestPayload(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int 