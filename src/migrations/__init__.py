from sqlmodel import Session, SQLModel, create_engine
from models.user import User

import config

engine = create_engine(config.DATABASE_URL)


def delete_db_and_tables():
    """
    Deletes the database and tables for the specified database URL.

    This function deletes the database and tables based on the provided
    database URL. It uses the `SQLModel.metadata.drop_all` method to drop the
    tables defined in the SQLAlchemy models.

    Args:
        None

    Returns:
        None

    """
    print(f"Deleting database and tables for {config.DATABASE_URL}")
    SQLModel.metadata.drop_all(engine)
    print("Database deleted")


def create_db_and_tables():
    """
    Creates the database and tables for the specified database URL.

    This function creates the necessary database and tables based on the provided
    database URL. It uses the `SQLModel.metadata.create_all` method to create the
    tables defined in the SQLAlchemy models.

    Args:
        None

    Returns:
        None

    """
    print(f"Creating database and tables for {config.DATABASE_URL}")
    SQLModel.metadata.create_all(engine)
    print("Database created")


def seed_db():
    """
    Seeds the database with a demo user.

    This function creates a new session, adds a demo user to the session,
    and commits the changes to the database.

    Parameters:
        None

    Returns:
        None
    """
    session = Session(engine)
    user = User(username="demo", is_active=True)
    session.add(user)
    session.commit()
