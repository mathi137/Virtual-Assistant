from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone
from pydantic import ConfigDict


class ClientBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    name: str
    email: str
    password: str


class Client(ClientBase, table=True):
    model_config = ConfigDict(extra='ignore')

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    email: str = Field(index=True, unique=True)
    password: str
    user_id: int = Field(foreign_key="user.id")
    disabled: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class ClientCreate(SQLModel):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "João Silva",
                "email": "joao@example.com",
                "password": "senha123",
                "system_prompt": "You are a helpful assistant for João Silva's business."
            }
        }
    )
    
    name: str
    email: str
    password: str
    system_prompt: Optional[str] = None  # Para criar o bot junto


class ClientRead(SQLModel):
    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "João Silva",
                "email": "joao@example.com",
                "user_id": 1,
                "disabled": False,
                "created_at": "2025-11-05T10:30:00Z"
            }
        }
    )
    
    id: int
    name: str
    email: str
    user_id: int
    disabled: bool
    created_at: datetime


class ClientUpdate(SQLModel):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "João Silva Jr.",
                "email": "joao.jr@example.com",
                "password": "novasenha123"
            }
        }
    )
    
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    disabled: Optional[bool] = None
