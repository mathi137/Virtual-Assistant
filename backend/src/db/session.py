from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings, get_logger
from src.db.crud import Database
from src.db.model.platform import Platform, platform_dict

logger = get_logger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def populate_model(session: AsyncSession, model: type[SQLModel], data: dict[int, str]):
    for id, name in data.items():
        existing_item = await Database.get(session, id, model)
        if not existing_item:
            item_model = model(id=id.value, name=name)
            try:
                await Database.create(session, item_model)
            except Exception as e:
                logger.warning(f"Item {id} already exists in {model.__name__}: {e}")
                pass


async def populate_db():
    async with get_session() as session:
        await populate_model(session, Platform, platform_dict)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    await populate_db()


async def close_db():
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session