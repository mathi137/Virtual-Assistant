import jwt
from typing import Annotated
from fastapi import HTTPException, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from src.config import settings
from src.db.session import get_session_dep
from src.db.crud import UserCRUD as Database
from src.db.model.user import User
from src.schemas.auth import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    db_user = await Database.get_user_by_email(session, email)
    if not db_user or not verify_password(password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db_user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session_dep)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if not user_id:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except InvalidTokenError:
        raise credentials_exception

    user = await Database.get(session=session, id=token_data.user_id, model=User)
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
