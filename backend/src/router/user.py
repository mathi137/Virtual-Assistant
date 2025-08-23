from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.model.user import User, UserBase, UserRead, UserUpdate
from src.db.session import get_session_dep
from src.db.crud import Database

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserBase, session: AsyncSession = Depends(get_session_dep)):
    # Create User instance from UserBase data
    user = User(**user_data.model_dump())
    return await Database.create(session, user)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session_dep)):
    return await Database.get(session, user_id, User)


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, session: AsyncSession = Depends(get_session_dep)):
    return await Database.update(session, user_id, user_update, User)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session_dep)):
    await Database.delete(session, user_id, User)
    return None