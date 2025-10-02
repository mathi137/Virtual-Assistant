from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict


class ChatBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    user_id: int
    agent_id: int
    platform_id: int


class Chat(ChatBase, table=True):
    model_config = ConfigDict(extra='ignore')
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    agent_id: int = Field(foreign_key="agent.id")
    platform_id: int = Field(foreign_key="platform.id")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatCreate(SQLModel):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "id": 12345,
                "user_id": 1,
                "agent_id": 1,
                "platform_id": 1
            }
        }
    )
    
    id: int
    user_id: int
    agent_id: int
    platform_id: int


class ChatRead(SQLModel):
    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "example": {
                "id": 12345,
                "user_id": 1,
                "agent_id": 1,
                "platform_id": 1,
                "created_at": "2025-09-07T10:30:00Z"
            }
        }
    )
    
    id: int
    user_id: int
    agent_id: int
    platform_id: int
    created_at: datetime