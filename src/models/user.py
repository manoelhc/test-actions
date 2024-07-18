from datetime import datetime
import uuid
from sqlmodel import Field, SQLModel
from pydantic import field_validator
from helpers.user import validate_user, validate_email


class UserCreate(SQLModel):
    """
    Represents a user creation request.

    Attributes:
        username (str): The username of the user to be created.
        email (str): The email of the user to be created.
    """

    username: str
    email: str

    @field_validator("username")
    @classmethod
    # skipcq: FLK-W505
    def username_check(cls, username: str):
        """Validates the username attribute.

        It validates the username attribute by stripping leading
            and trailing whitespace, converting it to lowercase,
            and checking its length and characters.

        Args:
            cls: The class instance.
            username (str): The value of the username attribute.

        Returns:
            str: The validated username.

        Raises:
            ValueError: If the username is less than 2 characters or
                contains non-alphanumeric characters.
        """
        username = username.strip().lower()
        if validate_user(username):
            return str(username)
        return None

    @field_validator("email")
    @classmethod
    def email_validator(cls, email: str) -> bool:
        return validate_email(email)


class User(UserCreate, table=True):
    # skipcq: FLK-W505
    """
    Represents a user entity.

    Attributes:
        id (uuid.UUID): The unique identifier of the user.
        username (str): The username of the user.
        is_active (bool): Indicates whether the user is active or not.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime | None): The timestamp when the user was last updated,
                                      or None if never updated.
        deleted_at (datetime | None): The timestamp when the user was deleted,
                                      or None if not deleted.
    """

    __tablename__ = "users"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        unique=True,
        index=True,
    )

    username: str = Field(default=None, index=True, unique=True, max_length=255)
    email: str = Field(default=None, index=False, unique=True, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=datetime.now(), nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)


class UserSimple(SQLModel):
    # skipcq: FLK-W505
    """
    Represents a simplified user entity.

    Attributes:
        username (str): The username of the user.
        id (uuid.UUID): The unique identifier of the user.
        is_active (bool): Indicates whether the user is active or not.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime | None): The timestamp when the user was last
                                      updated, or None if never updated.
    """

    username: str
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime | None


class UserUpdate(SQLModel):
    """
    Represents a user update request.

    Attributes:
        username (str): The updated username of the user.
        id (uuid.UUID): The unique identifier of the user.
        is_active (bool): Indicates whether the user is active or not.
    """

    username: str
    id: uuid.UUID
    is_active: bool
