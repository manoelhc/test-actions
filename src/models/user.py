from datetime import datetime
import uuid
import re
from sqlmodel import Field, SQLModel
from pydantic import field_validator


class UserCreate(SQLModel):
    username: str

    @field_validator("username")
    @classmethod
    def username_check(cls, v):
        username = v.strip().lower()
        if len(username) <= 2:
            raise ValueError("Username should be more than 2 characters")
        if re.match(r"^\w*$", username) is None:
            raise ValueError("Username must be alphanumeric and underscore only")
        return username


class User(UserCreate, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        unique=True,
        index=True,
    )
    username: str = Field(default=None, index=True, unique=True, max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=datetime.now(), nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)


class UserSimple(SQLModel):
    username: str
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class UserUpdate(SQLModel):
    username: str
    id: uuid.UUID
    is_active: bool
