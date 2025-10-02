from pydantic import BaseModel
from langchain_core.messages import AnyMessage

from langgraph.graph import add_messages
from typing import Annotated, Optional


class AgentState(BaseModel):
    messages: Annotated[list[AnyMessage], add_messages]
    query: str
    system_prompt: str
    client_name: Optional[str] = None
