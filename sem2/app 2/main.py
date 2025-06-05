from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api import auth, encode, websocket
from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine
import signal
import sys

def signal_handler(sig, frame):
    print('Shutting down gracefully...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Base.metadata.create_all(bind=engine) # Закомментировано, так как используется Alembic для миграций

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Перенаправление на документацию Swagger UI"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Проверка работоспособности сервера"""
    return {"status": "ok", "version": settings.VERSION}

#подключение маршрутов
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(encode.router, prefix=settings.API_V1_STR, tags=["encode"])
app.include_router(websocket.router, prefix=settings.API_V1_STR, tags=["websocket"]) 