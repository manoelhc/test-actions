from sqlmodel import SQLModel, create_engine
import config

engine = create_engine(config.DATABASE_URL)


def create_db_and_tables():
    print(f"Creating database and tables for {config.DATABASE_URL}")
    SQLModel.metadata.create_all(engine)
    print("Database created")


def seed_db():
    pass
