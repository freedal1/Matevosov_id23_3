# FastAPI WebSocket Task Manager

Проект для кодирования и декодирования данных с использованием WebSocket для отслеживания прогресса задач.

## Требования

- Python 3.8+
- pip (менеджер пакетов Python)
- Redis (для Celery)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd app
```

2. Создайте виртуальное окружение:
```bash
/usr/local/bin/python3.12 -m venv .venv
```

3. Активируйте виртуальное окружение:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/MacOS:
```bash
source .venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Примените миграции базы данных:
```bash
alembic upgrade head
```

6. Убедитесь, что Redis запущен:
```bash
# Проверка статуса Redis
redis-cli ping
```

## Запуск

1. Запустите Redis (если еще не запущен):
```bash
redis-server
```

2. Запустите Celery worker в отдельном терминале:
```bash
celery -A app.core.celery_app worker --loglevel=info
```

3. Запустите сервер:
```bash
uvicorn main:app --reload
```

4. Откройте в браузере:
- http://localhost:8000/docs - Swagger UI документация
- http://localhost:8000/redoc - ReDoc документация

## Использование

1. Зарегистрируйтесь через POST /api/v1/register
2. Получите токен через POST /api/v1/login
3. Используйте токен для авторизации в других запросах
4. Для WebSocket соединений используйте токен при подключении

## Структура проекта

```
app/
├── api/            # API endpoints
├── core/           # Core functionality
├── cruds/          # CRUD operations
├── db/             # Database configuration
├── models/         # Database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
└── tasks/          # Celery tasks
```

## WebSocket API

Подключение к WebSocket:
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${taskId}`);
```

Формат сообщений:
```json
{
  "status": "STARTED/PROGRESS/COMPLETED/FAILED",
  "task_id": "unique-task-id",
  "operation": "encode/decode",
  "progress": 50,  // для статуса PROGRESS
  "result": {      // для статуса COMPLETED
    "encoded_data": "base64_encoded_string",
    "huffman_codes": {
      "...": "..."
    },
    "padding": 4
  }
}
``` 