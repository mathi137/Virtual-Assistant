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
        # Ensure chat exists
        existing_chat = await Database.get(session, chat.id, Chat)
        if not existing_chat:
            try:
                # Validate that referenced entities exist before creating chat
                # Check if agent exists
                agent_exists = await Database.get(session, chat.agent_id, Agent)
                if not agent_exists:
                    raise ValueError(f"Agent with id {chat.agent_id} does not exist")
                
                chat_db = Chat(**chat.model_dump())
                await Database.create(session, chat_db)
                chat_id = chat.id
            except Exception as e:
                print(f"Error creating chat: {str(e)}")
                print(f"Chat data: {chat.model_dump()}")
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