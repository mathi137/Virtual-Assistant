from typing import Optional
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import SQLModel, Field


class MessageRole(Enum, str):
    USER = "user"
    AGENT = "agent"


class MessageBase(SQLModel):
    text: str
    role: MessageRole


class Message(MessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    text: str
    role: MessageRole = Field(default=MessageRole.USER)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageCreate(SQLModel):
    text: str


class MessageRead(SQLModel):
    id: int
    text: str
    role: MessageRole
    created_at: datetime