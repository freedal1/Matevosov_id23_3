from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import base64
import asyncio
from sqlalchemy.orm import Session
import uuid

from app.services.huffman import huffman_encode
from app.services.xor import xor_encrypt
from app.core.websocket import manager
from app.cruds.task import create_task, update_task, generate_task_id, get_task
from app.cruds.user import get_user_by_email
from app.db.session import get_db
from app.schemas.task import WebSocketMessage, TaskCreate, Task, EncodeRequestPayload, DecodeRequestPayload
from app.api.deps import get_current_user
from app.models.user import User
from app.tasks.encode import encode_task, decode_task

router = APIRouter()
#эндпоинты для кодирования и декодирования текста
class EncodeRequest(BaseModel):
    text: str
    key: str

class EncodeResponse(BaseModel):
    task_id: str

class DecodeRequest(BaseModel):
    encoded_data: str
    key: str
    huffman_codes: dict
    padding: int

class DecodeResponse(BaseModel):
    task_id: str

# Возвращаем async функции для обработки задач в фоне через BackgroundTasks
async def process_encode_task(
    task_id: str,
    text: str,
    key: str,
    user_id: int,
    db: Session
):
    try:
        # Отправка STARTED уведомления (если WebSocket менеджер поддерживает)
        await manager.send_task_update(
            user_id,
            task_id,
            WebSocketMessage(
                status="STARTED",
                task_id=task_id,
                operation="encode"
            )
        )

        # Имитация прогресса
        for progress in range(0, 101, 20):
            await asyncio.sleep(0.5)  # Имитация работы
            await manager.send_task_update(
                user_id,
                task_id,
                WebSocketMessage(
                    status="PROGRESS",
                    task_id=task_id,
                    operation="encode",
                    progress=progress
                )
            )

        # Выполнение кодирования
        encoded_text, huffman_codes, padding = huffman_encode(text)
        encrypted_text = xor_encrypt(encoded_text, key)
        encoded_data = base64.b64encode(encrypted_text.encode()).decode()

        result = {
            "encoded_data": encoded_data,
            "key": key,
            "huffman_codes": huffman_codes,
            "padding": padding
        }

        # Отправка COMPLETED уведомления
        await manager.send_task_update(
            user_id,
            task_id,
            WebSocketMessage(
                status="COMPLETED",
                task_id=task_id,
                operation="encode",
                result=result
            )
        )

        # Обновление задачи в базе данных
        update_task(db, task_id, {"status": "COMPLETED", "result": result})

    except Exception as e:
        # Отправка FAILED уведомления
        await manager.send_task_update(
            user_id,
            task_id,
            WebSocketMessage(
                status="FAILED",
                task_id=task_id,
                operation="encode",
                result={"error": str(e)}
            )
        )
        update_task(db, task_id, {"status": "FAILED", "result": {"error": str(e)}})

async def process_decode_task(
    task_id: str,
    encoded_data: str,
    key: str,
    huffman_codes: dict,
    padding: int,
    user_id: int,
    db: Session
):
    try:
        # Отправка STARTED уведомления
        await manager.send_task_update(
            user_id,
            task_id,
            WebSocketMessage(
                status="STARTED",
                task_id=task_id,
                operation="decode"
            )
        )

        # Имитация прогресса
        for progress in range(0, 101, 20):
            await asyncio.sleep(0.5)  # Имитация работы
            await manager.send_task_update(
                user_id,
                task_id,
                WebSocketMessage(
                    status="PROGRESS",
                    task_id=task_id,
                    operation="decode",
                    progress=progress
                )
            )

        # Выполнение декодирования
        encrypted_text = base64.b64decode(encoded_data).decode()
        decrypted_text = xor_encrypt(encrypted_text, key)
        decrypted_text = decrypted_text[:-padding] if padding > 0 else decrypted_text

        # Декодирование Хаффмана
        decoded_text = ""
        current_code = ""
        reverse_codes = {v: k for k, v in huffman_codes.items()}

        for bit in decrypted_text:
            current_code += bit
            if current_code in reverse_codes:
                decoded_text += reverse_codes[current_code]
                current_code = ""

        result = {"decoded_text": decoded_text}

        # Отправка COMPLETED уведомления
        await manager.send_task_update(
            user_id,
            task_id,
            WebSocketMessage(
                status="COMPLETED",
                task_id=task_id,
                operation="decode",
                result=result
            )
        )

        # Обновление задачи в базе данных
        update_task(db, task_id, {"status": "COMPLETED", "result": result})

    except Exception as e:
        # Отправка FAILED уведомления
        await manager.send_task_update(
            user_id,
            task_id,
            WebSocketMessage(
                status="FAILED",
                task_id=task_id,
                operation="decode",
                result={"error": str(e)}
            )
        )
        update_task(db, task_id, {"status": "FAILED", "result": {"error": str(e)}})

@router.post("/encode", response_model=Task)
async def encode(
    request_payload: EncodeRequestPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_id = str(uuid.uuid4())
    
    # Создание объекта TaskCreate для передачи в CRUD функцию
    task_create_data = TaskCreate(
        task_id=task_id,
        user_id=current_user.id,
        operation="encode",
        status="STARTED"
    )
    
    task = create_task(
        db,
        task=task_create_data
    )
    
    # Start Celery task
    encode_task.delay(
        task_id=task_id,
        text=request_payload.text,
        key=request_payload.key,
        user_id=current_user.id
    )
    
    return task

@router.post("/decode", response_model=Task)
async def decode(
    request_payload: DecodeRequestPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_id = str(uuid.uuid4())
    
    # Создание объекта TaskCreate для передачи в CRUD функцию
    task_create_data = TaskCreate(
        task_id=task_id,
        user_id=current_user.id,
        operation="decode",
        status="STARTED"
    )

    task = create_task(
        db,
        task=task_create_data
    )
    
    # Start Celery task
    decode_task.delay(
        task_id=task_id,
        encoded_data=request_payload.encoded_data,
        key=request_payload.key,
        huffman_codes=request_payload.huffman_codes,
        padding=request_payload.padding,
        user_id=current_user.id
    )
    
    return task 