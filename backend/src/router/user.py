from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.model.user import User, UserBase, UserRead, UserUpdate
from src.db.session import get_session_dep
from src.db.crud import UserCRUD as Database
from src.utils.auth import get_current_active_user, get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def get_all_users(session: AsyncSession = Depends(get_session_dep)):
    """
    Lista todos os usuários ativos do sistema.
    """
    return await Database.get_all_users(session)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserBase, session: AsyncSession = Depends(get_session_dep)):
    # Create User instance from UserBase data and hash password
    user = User(**user_data.model_dump())
    user.password = get_password_hash(user.password)
    return await Database.create(session, user)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session_dep)):
    return await Database.get(session, user_id, User)


@router.put("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update: UserUpdate, session: AsyncSession = Depends(get_session_dep)):
    # Password hashing is now handled automatically in the CRUD layer
    return await Database.update(session, user_id, user_update, User)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session_dep)):
    await Database.delete(session, user_id, User, UserUpdate)
    return None


@router.post("/{user_id}/reactivate", status_code=status.HTTP_200_OK)
async def reactivate_user(user_id: int, session: AsyncSession = Depends(get_session_dep)):
    await Database.reactivate(session, user_id, User, UserUpdate)
    return None


@router.get("/me/", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.put("/me/", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_me(current_user: Annotated[User, Depends(get_current_active_user)], user_update: UserUpdate, session: AsyncSession = Depends(get_session_dep)):
    # Password hashing is now handled automatically in the CRUD layer
    return await Database.update_user(session, current_user, user_update)


@router.delete("/me/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: Annotated[User, Depends(get_current_active_user)], session: AsyncSession = Depends(get_session_dep)):
    await Database.delete(session, current_user.id, User, UserUpdate)
    return None