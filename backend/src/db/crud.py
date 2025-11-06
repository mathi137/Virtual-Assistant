from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Type

from src.config import get_logger
from src.db.model.user import User, UserUpdate
from src.db.model.client import Client, ClientUpdate

logger = get_logger(__name__)

class Database:
    @staticmethod
    async def create(session: AsyncSession, item: SQLModel) -> SQLModel:
        try:
            session.add(item)
            await session.commit()
            await session.refresh(item)

        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            await session.rollback()
            raise HTTPException(status_code=400, detail="Item with given unique field already exists")
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            await session.rollback()
            raise HTTPException(status_code=400, detail="Unexpected error when creating item")
        return item


    @staticmethod
    async def get(session: AsyncSession, id: int, model: Type[SQLModel]) -> SQLModel | None:
        item = await session.get(model, id)
        if not item:
            logger.warning(f"Item with id {id} not found")
            return None
        if hasattr(item, "disabled") and item.disabled:
            logger.warning(f"Item with id {id} is disabled")
            return None
        return item


    @staticmethod
    async def update(session: AsyncSession, id: int, update_data: SQLModel, model: Type[SQLModel]) -> SQLModel:
        # Get the existing item first (this validates it exists)
        db_item = await Database.get(session, id, model)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Process update data
        if not isinstance(model, User):
            update_dict = update_data.model_dump(exclude_unset=True)
        
        # Update only the fields that are not None
        for field, value in update_dict.items():
            if value is not None:
                setattr(db_item, field, value)
        
        try:
            session.add(db_item)
            await session.commit()
            await session.refresh(db_item)
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_item
    

    @staticmethod
    async def delete(session: AsyncSession, id: int, model: Type[SQLModel], update_model: Type[SQLModel]) -> None:
        if hasattr(model, "disabled") is False:
            raise HTTPException(status_code=400, detail="Model does not support soft delete")
        return await Database.update(session, id, update_model(disabled=True), model)
    
    
    @staticmethod
    async def reactivate(session: AsyncSession, id: int, model: Type[SQLModel], update_model: Type[SQLModel]) -> None:
        if hasattr(model, "disabled") is False:
            raise HTTPException(status_code=400, detail="Model does not support reactivation")
        return await Database.update(session, id, update_model(disabled=False), model)
    

class UserCRUD(Database):
    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User:
        result = await session.exec(select(User).where(User.email == email))
        user = result.first()
        return user

    @staticmethod
    async def get_all_users(session: AsyncSession) -> list[User]:
        """
        Busca todos os usuários não desabilitados.
        """
        result = await session.exec(select(User).where(User.disabled == False))
        users = result.all()
        return users

    @staticmethod
    async def update(session: AsyncSession, user: User, update_data: UserUpdate) -> User:
        # Process update data
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated - import here to avoid circular import
        if 'password' in update_dict and update_dict['password'] is not None:
            from src.utils.auth import get_password_hash
            update_dict['password'] = get_password_hash(update_dict['password'])
        
        return await Database.update(session, user.id, UserUpdate(**update_dict), User)

class ClientCRUD(Database):
    @staticmethod
    async def get_all(session: AsyncSession) -> list[Client]:
        """Get all non-disabled clients."""
        result = await session.exec(select(Client).where(Client.disabled == False))
        return result.all()
    
    @staticmethod
    async def get_clients_by_user_id(session: AsyncSession, user_id: int) -> list[Client]:
        """Get all clients created by a specific user."""
        result = await session.exec(select(Client).where(Client.user_id == user_id, Client.disabled == False))
        return result.all()
    
    @staticmethod
    async def create(session: AsyncSession, client_data, user_id: int) -> Client:
        """Create a new client with hashed password."""
        from src.utils.auth import get_password_hash
        
        client_dict = client_data.model_dump(exclude={'system_prompt'})
        client_dict['password'] = get_password_hash(client_dict['password'])
        client_dict['user_id'] = user_id
        
        client = Client(**client_dict)
        return await Database.create(session, client)
