from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.model.user import User, UserRead
from src.db.session import get_session_dep
from src.db.crud import Database

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: User, session: AsyncSession = Depends(get_session_dep)):
    return await Database.create(session, user)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session_dep)):
    return await Database.get(session, User, user_id)
