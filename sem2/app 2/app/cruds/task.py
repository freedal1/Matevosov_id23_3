from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
import uuid

def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: str) -> Task:
    return db.query(Task).filter(Task.task_id == task_id).first()

def update_task(db: Session, task_id: str, task_update: TaskUpdate) -> Task:
    db_task = get_task(db, task_id)
    if db_task:
        if hasattr(task_update, 'model_dump'):
            update_data = task_update.model_dump(exclude_unset=True)
        else:
            update_data = task_update
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
    return db_task

def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()

def generate_task_id() -> str:
    return str(uuid.uuid4()) 