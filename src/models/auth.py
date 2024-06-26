from datetime import datetime
import uuid
import re
from sqlmodel import Field, SQLModel
from pydantic import field_validator


class Auth(SQLModel, table=True):
    __tablename__ = "auth"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        unique=True,
        index=True,
    )
    username_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        index=True,
    )
    password: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=datetime.now(), nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)

    @classmethod
    @field_validator("password")
    def password_check(cls, password: str):
        # Check if password is strong
        if len(password) < 8:
            raise ValueError("Password should be more than 8 characters")
        if (
            re.match(
                r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
                password,
            )
            is None
        ):
            raise ValueError(
                "Password must have at least one uppercase letter, one lowercase letter, one number, and one special character",
            )
        return True
