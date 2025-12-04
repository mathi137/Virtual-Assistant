from langgraph.checkpoint.mysql.aio import AIOMySQLSaver
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import settings
from src.db.model.message import MessageCreate
from src.db.model.chat import Chat, ChatCreate
from src.db.model.agent import Agent
from src.db.crud import Database
from src.agent.graph import AgentGraph
from src.config import get_logger

logger = get_logger(__name__)

async def process_message(session: AsyncSession, chat: ChatCreate, message: MessageCreate) -> str:
    """
    Process a user message and return an agent response.
    """
    try:
        # Look up chat by external_chat_id (Telegram/WhatsApp chat ID)
        from sqlmodel import select
        external_chat_id = chat.id  # This is the Telegram/WhatsApp chat ID
        statement = select(Chat).where(Chat.external_chat_id == external_chat_id)
        result = await session.exec(statement)
        existing_chat = result.first()
        
        if not existing_chat:
            try:
                # Validate that referenced entities exist before creating chat
                from src.db.model.user import User
                from src.db.model.platform import Platform
                
                # Check if user exists
                user_exists = await Database.get(session, chat.user_id, User)
                if not user_exists:
                    raise ValueError(f"User with id {chat.user_id} does not exist")
                
                # Check if agent exists
                agent_exists = await Database.get(session, chat.agent_id, Agent)
                if not agent_exists:
                    raise ValueError(f"Agent with id {chat.agent_id} does not exist")
                
                # Check if platform exists
                platform_exists = await Database.get(session, chat.platform_id, Platform)
                if not platform_exists:
                    raise ValueError(f"Platform with id {chat.platform_id} does not exist")
                
                # Create chat with external_chat_id, let database auto-generate id
                chat_data = chat.model_dump()
                chat_data['external_chat_id'] = chat_data.pop('id')  # Move id to external_chat_id
                chat_db = Chat(**chat_data)
                await Database.create(session, chat_db)
                await session.refresh(chat_db)
                chat_id = chat_db.id
            except Exception as e:
                logger.error(f"Error creating chat: {str(e)}")
                logger.error(f"Chat data: {chat.model_dump()}")
                raise e
        else:
            chat_id = existing_chat.id
    except Exception as e:
        logger.exception("Error creating chat")
        raise e

    try:
        # Get agent configuration
        agent_db = await Database.get(session, chat.agent_id, Agent)
        if not agent_db:
            raise ValueError(f"Agent with id {chat.agent_id} not found")

        config = {"configurable": {"thread_id": chat_id}}

        # Prepare the input state for the agent
        agent_input = {
            "messages": [],
            "query": message.text,
            "system_prompt": agent_db.system_prompt if hasattr(agent_db, 'system_prompt') else "You are a helpful assistant.",
            "client_name": message.client_name,
        }

        # Create graph and config
        agent_graph = AgentGraph()

        async with AIOMySQLSaver.from_conn_string(settings.DATABASE_URL) as checkpointer:
            app = await agent_graph.build_graph(checkpointer)

            # Process through the graph
            response = await app.ainvoke(agent_input, config=config)
        
        # Extract the last AI message
        last_message = response["messages"][-1]
        response_text = last_message.content if hasattr(last_message, "content") else str(last_message)

        return response_text
    
    except Exception:
        logger.exception("Error processing message")
        return "I'm sorry, I encountered an error while processing your message. Please try again."