from sqlmodel import Session, SQLModel, create_engine, select
from models.user import User
from models.auth import Auth
import uuid

import config

engine = create_engine(config.DATABASE_URL)


def delete_db_and_tables():
    """Deletes the database and tables for the specified database URL.

    This function deletes the database and tables based on the provided
    database URL. It uses the `SQLModel.metadata.drop_all` method to drop the
    tables defined in the SQLAlchemy models.
    """
    print("Deleting database and tables...")
    SQLModel.metadata.drop_all(engine)
    print("Database deleted")


def create_db_and_tables():
    """Creates the database and tables for the specified database URL.

    This function creates the necessary database and tables based on the provided
    database URL. It uses the `SQLModel.metadata.create_all` method to create the
    tables defined in the SQLAlchemy models.
    """
    print("Deleting database and tables...")
    SQLModel.metadata.create_all(engine)
    print("Database created")


def seed_db():
    """Seeds the database with a demo user.

    This function creates a new session, adds a demo user to the session,
    and commits the changes to the database.
    """
    print("Seeding DB")
    default_username = "admin"
    # ruff: noqa: B105
    default_password = f"{uuid.uuid4()}!8"

    session = Session(engine)
    user = User(
        username=default_username,
        email=f"{default_username}@example.com",
        is_active=True,
    )
    session.add(user)
    session.commit()

    user = session.exec(
        select(User).where(
            User.username == default_username,
            User.email == f"{default_username}@example.com",
            # ruff: noqa: E712
            User.is_active == True,
            # ruff: noqa: E711
            User.deleted_at == None,
        ),
    ).first()

    session = Session(engine)
    auth = Auth(username_id=user.id, password=default_password)
    session.add(auth)
    session.commit()
