from fastapi import HTTPException
from sqlmodel import SQLModel, select
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Type, Union

from src.config import get_logger
from src.db.model.user import User, UserUpdate
from src.db.model.agent import Agent, AgentRead, AgentCreate, AgentUpdate, Token
from src.db.model.message import Message

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
    async def get(session: AsyncSession, id: Union[int, str], model: Type[SQLModel]) -> SQLModel | None:
        item = await session.get(model, id)
        if not item:
            logger.warning(f"Item with id {id} not found")
            return None
        if hasattr(item, "disabled") and item.disabled:
            logger.warning(f"Item with id {id} is disabled")
            return None
        return item


    @staticmethod
    async def update(session: AsyncSession, id: Union[int, str], update_data: SQLModel, model: Type[SQLModel]) -> SQLModel:
        # Get the existing item first (this validates it exists)
        db_item = await Database.get(session, id, model)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Process update data
        if not isinstance(model, User):
            update_dict = update_data.model_dump(exclude_unset=True)
        else:
            # For User model, handle password hashing
            update_dict = update_data.model_dump(exclude_unset=True)
            if 'password' in update_dict and update_dict['password'] is not None:
                from src.utils.auth import get_password_hash
                update_dict['password'] = get_password_hash(update_dict['password'])
        
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
    async def delete(session: AsyncSession, id: Union[int, str], model: Type[SQLModel], update_model: Type[SQLModel]) -> None:
        if hasattr(model, "disabled") is False:
            raise HTTPException(status_code=400, detail="Model does not support soft delete")
        return await Database.update(session, id, update_model(disabled=True), model)
    
    
    @staticmethod
    async def reactivate(session: AsyncSession, id: Union[int, str], model: Type[SQLModel], update_model: Type[SQLModel]) -> None:
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
    async def update(session: AsyncSession, user: User, update_data: UserUpdate) -> User:
        # Process update data
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated - import here to avoid circular import
        if 'password' in update_dict and update_dict['password'] is not None:
            from src.utils.auth import get_password_hash
            update_dict['password'] = get_password_hash(update_dict['password'])
        
        return await Database.update(session, user.id, UserUpdate(**update_dict), User)


class MessageCRUD(Database):
    @staticmethod
    async def get_messages_by_chat_id(session: AsyncSession, chat_id: int, limit: int = 20) -> list[Message]:
        """
        Get messages for a specific chat, ordered by creation time (oldest first).
        """
        try:
            statement = (
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            result = await session.exec(statement)
            messages = result.all()
            # Reverse to get chronological order (oldest first)
            return list(reversed(messages))
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return []
        

class AgentCRUD(Database):
    @staticmethod
    async def get(session: AsyncSession, id: Union[int, str]) -> AgentRead | None:
        agent_db = await Database.get(session, id, Agent)
        if not agent_db:
            logger.warning(f"Item with id {id} not found")
            return None
        
        # Allow fetching disabled agents
        if hasattr(agent_db, "disabled") and agent_db.disabled:
            logger.warning(f"Item with id {id} is disabled")
            return None

        # Convert agent data to dict and handle tokens conversion
        agent_data = agent_db.model_dump()
        
        # Convert raw JSON tokens to Token objects if they exist
        if agent_data.get('tokens'):
            agent_data['tokens'] = [Token(**token) for token in agent_data['tokens']]
        
        agent_read = AgentRead(**agent_data)
        return agent_read
    

    @staticmethod
    async def create(session: AsyncSession, item: AgentCreate) -> AgentRead:
        # Convert AgentCreate data to dict and handle tokens
        agent_data = item.model_dump()
        
        # Convert Token objects to raw dict for database storage
        if agent_data.get('tokens'):
            agent_data['tokens'] = [token.model_dump() if hasattr(token, 'model_dump') else token 
                                  for token in agent_data['tokens']]
        
        agent_instance = Agent(**agent_data)
        created_agent = await Database.create(session, agent_instance)
        return await AgentCRUD.get(session, created_agent.id)


    @staticmethod
    async def update(session: AsyncSession, id: Union[int, str], update_data: AgentUpdate) -> AgentRead:
        await Database.update(session, id, update_data, Agent)
        return await AgentCRUD.get(session, id)


    @staticmethod
    async def get_agents_by_user_id(session: AsyncSession, user_id: str) -> list[Agent]:
        try:
            statement = select(Agent).where(Agent.user_id == user_id)
            result = await session.exec(statement)
            agents = result.all()
            return agents
        except Exception as e:
            logger.error(f"Error getting agents for user {user_id}: {e}")
            return []