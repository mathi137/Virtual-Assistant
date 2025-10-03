from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field


class ChatBase(SQLModel):
    user_id: int
    # agent_id: int
    platform_id: int


class Chat(ChatBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # agent_id: int = Field(foreign_key="agent.id")
    platform_id: int = Field(foreign_key="platform.id")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatCreate(SQLModel):
    user_id: int
    # agent_id: int
    platform_id: int


class ChatRead(SQLModel):
    id: int
    user_id: int
    # agent_id: int
    platform_id: int
    created_at: datetime