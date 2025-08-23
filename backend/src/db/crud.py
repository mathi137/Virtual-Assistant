from fastapi import HTTPException
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Type

class Database:
    @staticmethod
    async def create(session: AsyncSession, item: Type[SQLModel]):
        try:
            session.add(item)
            await session.commit()
            await session.refresh(item)
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return item

    @staticmethod
    async def get(session: AsyncSession, model: Type[SQLModel], id: int):
        item = await session.get(model, id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item