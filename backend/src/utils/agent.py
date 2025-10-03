from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.model.message import Message, MessageCreate, MessageRole
from src.db.model.chat import Chat
from src.db.crud import Database

async def process_message(session: AsyncSession, message: MessageCreate, user_id: int, chat_id: int) -> str:
    """
    Process a user message and return an agent response.
    """
    if not (await Database.get(session, chat_id, Chat)):
        chat_model = Chat(id=chat_id, user_id=user_id)
        await Database.create(session, chat_model)

    user_message_model = Message(chat_id=chat_id, **message.__dict__)
    await Database.create(session, user_message_model)

    response = f"Agent: {user_message_model.text}"
    agent_message_model = Message(chat_id=chat_id, text=response, role=MessageRole.AGENT)
    await Database.create(session, agent_message_model)

    # Echo message for now
    return agent_message_model.text