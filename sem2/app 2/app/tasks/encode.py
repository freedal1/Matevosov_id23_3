from app.core.celery_app import celery_app
from app.services.huffman import huffman_encode
from app.services.xor import xor_encrypt
from app.cruds.task import update_task
from app.db.session import SessionLocal

import base64

@celery_app.task
def encode_task(
    task_id: str,
    text: str,
    key: str,
    user_id: int
):
    db = SessionLocal()
    try:
        # Simulate progress updates (optional in Celery, but kept for consistency)
        for progress in range(0, 101, 20):
            # In a real Celery app, you might update task status here, e.g., task.update_state()
            # For now, we'll just simulate work if needed
            pass # asyncio.sleep(0.5) # Cannot use await in a standard Celery task

        # Perform encoding
        encoded_text, huffman_codes, padding = huffman_encode(text)
        encrypted_text = xor_encrypt(encoded_text, key)
        encoded_data = base64.b64encode(encrypted_text.encode()).decode()

        result = {
            "encoded_data": encoded_data,
            "key": key,
            "huffman_codes": huffman_codes,
            "padding": padding
        }

        # Обновление задачи в базе данных
        update_task(db, task_id, {"status": "COMPLETED", "result": result})

    except Exception as e:
        update_task(db, task_id, {"status": "FAILED", "result": {"error": str(e)}})
    finally:
        db.close()

@celery_app.task
def decode_task(
    task_id: str,
    encoded_data: str,
    key: str,
    huffman_codes: dict,
    padding: int,
    user_id: int
):
    db = SessionLocal()
    try:
        # Simulate progress updates (optional in Celery)
        for progress in range(0, 101, 20):
             pass # asyncio.sleep(0.5)

        # Perform decoding
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

        # Обновление задачи в базе данных
        update_task(db, task_id, {"status": "COMPLETED", "result": result})

    except Exception as e:
        update_task(db, task_id, {"status": "FAILED", "result": {"error": str(e)}})
    finally:
        db.close() 