from pydantic import BaseModel
from typing import Optional, Dict


class Chat(BaseModel):
    id: int
    type: str


class Message(BaseModel):
    message_id: int
    chat: Chat
    from_user: Optional[Dict] = None
    text: str | None = None


class Update(BaseModel):
    update_id: int
    message: Message | None = None


class Token(BaseModel):
    platform_id: int
    platform_name: str
    token: str


class AgentEvent(BaseModel):
    id: int
    user_id: int
    system_prompt: str
    disabled: bool
    tokens: list[Token] | None = None
    created_at: str | None = None


class AgentWebhookPayload(BaseModel):
    event: str  # 'created' or 'deleted'
    agent: AgentEvent

