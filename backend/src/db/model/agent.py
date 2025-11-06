from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone


class Agent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    system_prompt: str = Field(default="You are a helpful assistant.")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
