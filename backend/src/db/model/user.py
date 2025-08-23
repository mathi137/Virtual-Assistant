from sqlmodel import Field, SQLModel
from typing import Optional
from pydantic import model_validator, ConfigDict


class UserBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    email: str
    password: str


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)


class UserRead(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    id: int
    email: str


class UserUpdate(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    email: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_at_least_one_field(cls, values):
        if isinstance(values, dict):
            # Check if at least one field has a non-None value
            if not any(value is not None for value in values.values()):
                raise ValueError("At least one field must be provided for update")
        return values