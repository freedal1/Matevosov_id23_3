import requests
import websockets
import asyncio
import json
import unicodedata

API_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/api/v1/ws/{task_id}"

def clean_string(text):
    """Удаляет символы, невалидные для UTF-8."""
    # Попытка нормализации и удаления невалидных символов
    try:
        # Нормализация Unicode (NFC - Canonical Composition)
        normalized_text = unicodedata.normalize('NFC', text)
        # Удаление символов, которые не могут быть представлены в UTF-8
        # (например, непарные суррогаты)В
        cleaned_text = normalized_text.encode('utf-8', 'ignore').decode('utf-8')
        return cleaned_text
    except Exception:
        # Если нормализация или кодирование вызывает ошибку, просто пытаемся кодировать с ignore
        return text.encode('utf-8', 'ignore').decode('utf-8')

def login(email, password):
    cleaned_email = clean_string(email)
    cleaned_password = clean_string(password)
    resp = requests.post(f"{API_URL}/api/v1/login/", data={"username": cleaned_email, "password": cleaned_password})
    resp.raise_for_status()
    return resp.json()["access_token"]

def start_encode(token, text, key):
    resp = requests.post(
        f"{API_URL}/api/v1/encode",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": text, "key": key}
    )
    resp.raise_for_status()
    return resp.json()["task_id"]

async def listen_ws(token, task_id):
    async with websockets.connect(
        WS_URL.format(task_id=task_id),
        extra_headers={"Authorization": f"Bearer {token}"}
    ) as ws:
        print(f"[WebSocket] Listening for task_id={task_id}")
        try:
            async for message in ws:
                print(f"[Notification][{task_id}]", message)
        except websockets.ConnectionClosed:
            print(f"[WebSocket] Connection closed for task_id={task_id}")

if __name__ == "__main__":
    import getpass
    email = input("Email: ")
    password = getpass.getpass("Password: ")
    text = input("Text to encode: ")
    key = input("Key: ")
    token = login(email, password)
    task_id = start_encode(token, text, key)
    print(f"Started encode task with id: {task_id}")
    asyncio.run(listen_ws(token, task_id)) 