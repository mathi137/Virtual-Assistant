from typing import Optional
from enum import Enum, auto

from sqlmodel import SQLModel, Field


class PlatformID(Enum):
    TELEGRAM = auto()
    WHATSAPP = auto()


platform_dict: dict[PlatformID, str] = {
    PlatformID.TELEGRAM: "telegram",
    PlatformID.WHATSAPP: "whatsapp",
}


class PlatformBase(SQLModel):
    name: str


class Platform(PlatformBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
