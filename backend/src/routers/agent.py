from typing import Annotated
from fastapi import APIRouter, Depends, status

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.session import get_session_dep
from src.db.model.message import MessageCreate
from src.db.model.agent import Agent, AgentRead, AgentCreate, AgentUpdate
from src.db.model.chat import ChatCreate
from src.db.crud import AgentCRUD as Database
from src.controllers.chat import process_message

router = APIRouter()


@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.create(session, agent)


@router.get("/{agent_id}", response_model=AgentRead, status_code=status.HTTP_200_OK)
async def get_agent(agent_id: int, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.get(session, agent_id)


@router.put("/{agent_id}", response_model=AgentRead, status_code=status.HTTP_200_OK)
async def update_agent(agent_id: int, agent_update: AgentUpdate, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.update(session, agent_id, agent_update)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, session: Annotated[AsyncSession, Depends(get_session_dep)]):
    return await Database.delete(session, agent_id, Agent, AgentUpdate)


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
        "agent_response": response
    }