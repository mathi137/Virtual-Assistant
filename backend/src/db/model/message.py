from typing import Optional
from datetime import datetime, timezone
from enum import Enum, auto

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict

class MessageRole(Enum):
    CLIENT = auto()
    AGENT = auto()
    USER = auto()


message_role_dict: dict[MessageRole, str] = {
    MessageRole.CLIENT: "client",
    MessageRole.AGENT: "agent",
    MessageRole.USER: "user",
}


class MessageBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    text: str
    client_name: Optional[str] = None
    role: MessageRole


class Message(MessageBase, table=True):
    model_config = ConfigDict(extra='ignore')
    
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    text: str = Field(max_length=4096)
    client_name: Optional[str] = Field(default=None)
    role: MessageRole = Field(default=MessageRole.USER, index=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageCreate(SQLModel):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "client_name": "john_doe",
                "text": "Hello, how can you help me today?"
            }
        }
    )
    
    client_name: Optional[str] = None
    text: str


class MessageRead(SQLModel):
    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "example": {
                "id": 1,
                "text": "Hello, how can you help me today?",
                "client_name": "john_doe",
                "role": "CLIENT",
                "created_at": "2025-09-07T10:30:00Z"
            }
        }
    )
    
    id: int
    text: str
    client_name: Optional[str]
    role: MessageRole
    created_at: datetime