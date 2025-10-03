from typing import Annotated
from fastapi import APIRouter, Depends, status

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.session import get_session_dep
from src.db.model.message import MessageCreate
from src.utils.agent import process_message

router = APIRouter()


@router.post("/chat/{chat_id}/{user_id}", status_code=status.HTTP_200_OK)
async def chat_with_agent(
    chat_id: int,
    user_id: int,
    message: MessageCreate,
    session: Annotated[AsyncSession, Depends(get_session_dep)]
):
    """
    Endpoint to handle chat messages with an agent.
    """
    response = await process_message(session, message, user_id, chat_id)
    
    return {
        "agent_response": response
    }