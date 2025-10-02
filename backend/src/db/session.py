from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from langgraph.checkpoint.mysql.aio import AIOMySQLSaver

from src.config import settings
from src.db.crud import Database
from src.db.model.platform import Platform, platform_dict

engine = create_async_engine(settings.DATABASE_URL, isolation_level="AUTOCOMMIT")

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)



async def populate_model(session: AsyncSession, model: type[SQLModel], data: dict):
    for platform_id, name in data.items():
        # Use the enum value as the database ID
        db_id = platform_id.value
        existing_item = await Database.get(session, db_id, model)
        if not existing_item:
            item_model = model(id=db_id, name=name)
            await Database.create(session, item_model)


async def populate_db():
    async with get_session() as session:
        await populate_model(session, Platform, platform_dict)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AIOMySQLSaver.from_conn_string(settings.DATABASE_URL) as checkpointer:
        await checkpointer.setup()


async def close_db():
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
