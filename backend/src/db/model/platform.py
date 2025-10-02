from typing import Optional
from enum import Enum, auto

from sqlmodel import SQLModel, Field
from pydantic import ConfigDict


class PlatformID(Enum):
    TELEGRAM = auto()
    WHATSAPP = auto()


platform_dict: dict[PlatformID, str] = {
    PlatformID.TELEGRAM: "telegram",
    PlatformID.WHATSAPP: "whatsapp",
}


class PlatformBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    name: str


class Platform(PlatformBase, table=True):
    model_config = ConfigDict(extra='ignore')
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)


class PlatformCreate(SQLModel):
    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={
            "example": {
                "name": "telegram"
            }
        }
    )
    
    name: str


class PlatformRead(SQLModel):
    model_config = ConfigDict(
        extra='ignore',
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "telegram"
            }
        }
    )
    
    id: int
    name: str
