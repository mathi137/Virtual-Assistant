from enum import StrEnum

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph.state import RunnableConfig

from src.agent.state import AgentState
from src.config import get_logger
from src.db.session import get_session
from src.db.model.message import Message, MessageRole
from src.db.crud import Database

logger = get_logger(__name__)

llm = ChatOpenAI(model="gpt-5-nano")


class AgentNodes(StrEnum):
    ENTRY = "entry"
    ANSWER = "answer"
    SAVE_MESSAGE = "save_message"


async def entry_node(state: AgentState) -> dict:
    """
    Node to get the entry message from the database.
    """
    return { "messages": [HumanMessage(content=state.query, name=state.client_name or "client")] }


async def answer_node(state: AgentState) -> dict:
    """
    Node to get an answer from the LLM.
    """
    ai_message = await llm.ainvoke(
        [SystemMessage(content=state.system_prompt), *state.messages],
    )

    return { "messages": [ai_message] }


async def save_message_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    Node to save the message to the database.
    """
    chat_id = config.get("configurable", {}).get("thread_id")

    if not chat_id:
        raise ValueError("thread_id not found in config")

    ai_message = state.messages[-1]
    user_message = state.query

    # Create and save user message
    async with get_session() as session:
        user_message_db = Message(
            chat_id=chat_id, 
            text=user_message,
            client_name=state.client_name,
            role=MessageRole.CLIENT
        )
        await Database.create(session, user_message_db)

        # Save agent response
        agent_message_db = Message(
            chat_id=chat_id, 
            text=ai_message.content, 
            role=MessageRole.AGENT
        )
        await Database.create(session, agent_message_db)

    return {}
