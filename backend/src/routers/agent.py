from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.session import get_session_dep
from src.db.model.agent import Agent, AgentRead, AgentCreate, AgentUpdate
from src.db.model.message import MessageCreate
from src.db.model.chat import ChatCreate
from src.db.crud import AgentCRUD as Database
from src.controllers.chat import process_message

router = APIRouter()


@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.create(session, agent)


@router.get("/", response_model=list[AgentRead], status_code=status.HTTP_200_OK)
async def get_all_active_agents(session: Annotated[AsyncSession, Depends(get_session_dep)]):
    """Get all active agents (not disabled, not deleted)."""
    return await Database.get_all_active_agents(session)


@router.get("/{agent_id}", response_model=AgentRead, status_code=status.HTTP_200_OK)
async def get_agent(agent_id: int, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    item = await Database.get(session, agent_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return item


@router.put("/{agent_id}", response_model=AgentRead, status_code=status.HTTP_200_OK)
async def update_agent(agent_id: int, agent_update: AgentUpdate, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.update(session, agent_id, agent_update)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    # Get agent data directly from database (bypass disabled check) for webhook
    from src.db.model.agent import Token
    from src.db.crud import Database as BaseDatabase
    from src.utils.webhook import trigger_agent_webhook
    from src.config import get_logger
    
    logger = get_logger(__name__)
    
    # Use session.get() directly to bypass disabled check
    agent_db = await session.get(Agent, agent_id)
    if not agent_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    # Convert agent data to dict for webhook (before deletion)
    agent_data = agent_db.model_dump()
    
    # Convert raw JSON tokens to Token objects if they exist
    if agent_data.get('tokens'):
        agent_data['tokens'] = [Token(**token) for token in agent_data['tokens']]
    
    agent_read = AgentRead(**agent_data)
    agent_dict = agent_read.model_dump()
    
    # Convert datetime to string for JSON serialization
    if 'created_at' in agent_dict and agent_dict['created_at']:
        agent_dict['created_at'] = agent_dict['created_at'].isoformat()
    
    # Perform deletion (soft delete) - use BaseDatabase for the delete method
    await BaseDatabase.delete(session, agent_id, Agent, AgentUpdate)
    
    # Trigger webhook for agent deletion (non-blocking - log errors but don't fail)
    try:
        webhook_success = await trigger_agent_webhook('deleted', agent_dict)
        if not webhook_success:
            logger.warning(f"Webhook for agent deletion failed, but agent {agent_id} was deleted from database")
    except Exception as e:
        logger.error(f"Error triggering webhook for agent deletion: {e}", exc_info=True)
        # Don't fail the deletion if webhook fails
    
    return None


@router.get("/user/{user_id}", response_model=list[Agent], status_code=status.HTTP_200_OK)
async def get_agent_by_user(user_id: str, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.get_agents_by_user_id(session, user_id)


@router.post("/chat/", status_code=status.HTTP_200_OK)
async def chat_with_agent(
    chat: ChatCreate,
    message: MessageCreate,
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """
    Endpoint to handle chat messages with an agent.
    """
    response = await process_message(session, chat, message)
    
    return {
        "response": response
    }