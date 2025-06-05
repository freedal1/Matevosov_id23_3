from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import oauth2_scheme, get_token_data
from app.cruds.user import get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.core.config import get_redis_client
#получаем текцщего пользователя
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Проверка токена в Redis
    redis_client = get_redis_client()
    if not redis_client.exists(token):
        raise credentials_exception
    token_data = get_token_data(token)
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user 