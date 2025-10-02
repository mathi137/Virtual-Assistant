from typing import Optional, Any
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from pydantic import ConfigDict


class AgentBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    user_id: int
    system_prompt: str
    disabled: bool


class Token(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    platform_id: int
    platform_name: str
    token: str


class Agent(AgentBase, table=True):
    model_config = ConfigDict(extra='ignore')
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    system_prompt: str = Field(default=None, max_length=4096)
    disabled: bool = Field(default=False)
    tokens: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCreate(SQLModel):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "user_id": 1,
                "system_prompt": "You are a helpful AI assistant. Be concise and accurate in your responses.",
                "tokens": [
                    {
                        "platform_id": 1,
                        "platform_name": "telegram",
                        "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                    }
                ]
            }
        }
    )
    
    user_id: int
    system_prompt: str
    tokens: Optional[list[Token]] = Field(default=None)


class AgentRead(SQLModel):
    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 1,
                "system_prompt": "You are a helpful AI assistant. Be concise and accurate in your responses.",
                "disabled": False,
                "tokens": [
                    {
                        "platform_id": 1,
                        "platform_name": "telegram",
                        "token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                    }
                ],
                "created_at": "2025-09-07T10:30:00Z"
            }
        }
    )

    id: int
    user_id: int
    system_prompt: str
    disabled: bool
    tokens: Optional[list[Token]] = Field(default=None)
    created_at: datetime


class AgentUpdate(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    system_prompt: Optional[str] = None
    disabled: Optional[bool] = None
    tokens: Optional[list[Token]] = Field(default=None)