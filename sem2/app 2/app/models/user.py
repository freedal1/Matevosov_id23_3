from sqlalchemy import Boolean, Column, Integer, String
from app.db.base_class import Base
#модель пользователя
class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True) 