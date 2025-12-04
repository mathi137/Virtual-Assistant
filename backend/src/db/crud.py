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
            logger.error(f"Integrity error: {e}", exc_info=True)
            await session.rollback()
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            
            # Check for foreign key constraint violations
            if "foreign key" in error_msg.lower() or "FOREIGN KEY" in str(e):
                if "user.id" in error_msg or "user_id" in error_msg.lower():
                    raise HTTPException(
                        status_code=400, 
                        detail=f"User with the provided user_id does not exist. Please ensure the user is registered first."
                    )
                else:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Referenced entity does not exist: {error_msg}"
                    )
            # Check for unique constraint violations
            elif "unique" in error_msg.lower() or "UNIQUE" in str(e):
                raise HTTPException(
                    status_code=400, 
                    detail="Item with given unique field already exists"
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Database constraint violation: {error_msg}"
                )
        except Exception as e:
            logger.error(f"Error creating item: {e}", exc_info=True)
            await session.rollback()
            error_msg = str(e)
            # Provide more specific error messages based on exception type
            if "foreign key" in error_msg.lower():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Referenced entity does not exist: {error_msg}"
                )
            raise HTTPException(
                status_code=400, 
                detail=f"Error creating item: {error_msg}"
            )
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
        # Note: User validation is now handled at the router level through authentication
        # This method assumes the user_id is valid (set by the authenticated endpoint)
        
        # Convert AgentCreate data to dict and handle tokens
        agent_data = item.model_dump()
        
        # Convert Token objects to raw dict for database storage
        if agent_data.get('tokens'):
            agent_data['tokens'] = [token.model_dump() if hasattr(token, 'model_dump') else token 
                                  for token in agent_data['tokens']]
        
        agent_instance = Agent(**agent_data)
        created_agent = await Database.create(session, agent_instance)
        agent_read = await AgentCRUD.get(session, created_agent.id)
        
        # Trigger webhook for agent creation
        if agent_read:
            from src.utils.webhook import trigger_agent_webhook
            agent_dict = agent_read.model_dump()
            # Convert datetime to string for JSON serialization
            if 'created_at' in agent_dict and agent_dict['created_at']:
                agent_dict['created_at'] = agent_dict['created_at'].isoformat()
            await trigger_agent_webhook('created', agent_dict)
        
        return agent_read


    @staticmethod
    async def update(session: AsyncSession, id: Union[int, str], update_data: AgentUpdate) -> AgentRead:
        await Database.update(session, id, update_data, Agent)
        return await AgentCRUD.get(session, id)


    @staticmethod
    async def get_agents_by_user_id(session: AsyncSession, user_id: str) -> list[Agent]:
        """Get all enabled agents for a specific user."""
        try:
            statement = select(Agent).where(
                Agent.user_id == user_id,
                Agent.disabled == False
            )
            result = await session.exec(statement)
            agents = result.all()
            return agents
        except Exception as e:
            logger.error(f"Error getting agents for user {user_id}: {e}")
            return []
    
    @staticmethod
    async def get_all_active_agents(session: AsyncSession) -> list[AgentRead]:
        """Get all active agents (not disabled, not deleted)."""
        try:
            statement = select(Agent).where(Agent.disabled == False)
            result = await session.exec(statement)
            agents = result.all()
            
            # Convert to AgentRead format
            agent_reads = []
            for agent_db in agents:
                agent_data = agent_db.model_dump()
                # Convert raw JSON tokens to Token objects if they exist
                if agent_data.get('tokens'):
                    agent_data['tokens'] = [Token(**token) for token in agent_data['tokens']]
                agent_read = AgentRead(**agent_data)
                agent_reads.append(agent_read)
            
            return agent_reads
        except Exception as e:
            logger.error(f"Error getting all active agents: {e}")
            return []