from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base

class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    operation = Column(String)  # "encode" or "decode"
    status = Column(String)  # "STARTED", "PROGRESS", "COMPLETED", "FAILED"
    progress = Column(Integer, default=0)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 