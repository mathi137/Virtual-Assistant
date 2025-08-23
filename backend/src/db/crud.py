from fastapi import HTTPException
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Type

from src.config import get_logger

logger = get_logger(__name__)

class Database:
    @staticmethod
    async def create(session: AsyncSession, item: SQLModel):
        try:
            session.add(item)
            await session.commit()
            await session.refresh(item)
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return item

    @staticmethod
    async def get(session: AsyncSession, id: int, model: Type[SQLModel]):
        item = await session.get(model, id)
        if not item:
            logger.error(f"Item with id {id} not found")
            raise HTTPException(status_code=404, detail="Item not found")
        return item
    
    @staticmethod
    async def update(session: AsyncSession, id: int, update_data: SQLModel, model: Type[SQLModel]):
        # Get the existing item
        db_item = await Database.get(session, id, model)
        
        # Update only the fields that are not None
        update_dict = update_data.model_dump(exclude_unset=True)
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
    async def delete(session: AsyncSession, id: int, model: Type[SQLModel]):
        db_item = await Database.get(session, id, model)
        
        try:
            await session.delete(db_item)
            await session.commit()
        except Exception as e:
            logger.error(f"Error deleting item: {e}")
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))