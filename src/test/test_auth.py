from fastapi.testclient import TestClient
from migrations import create_db_and_tables, delete_db_and_tables, engine
from app import app
from helpers.auth import get_password_hash
import pytest
from models.auth import Auth
from models.user import User


@pytest.fixture
def client():
    """This function creates a database and tables, seeds the database,
    creates a TestClient for the application, yields the client for testing,
    deletes the database and tables, and closes the client.

    Yields:
        TestClient: A client for testing the application.
    """
    create_db_and_tables()
    # seed_db()
    client = TestClient(app)
    yield client
    delete_db_and_tables()
    # os.unlink('data/test_db')
    client.close()


def get_activation_token(username):
    conn = engine.raw_connection()
    cur = conn.cursor()
    # no-qa: B608
    res = cur.execute(
        f"SELECT id FROM {User.__tablename__} where username = ?",
        (username,),
    )
    user_id = res.fetchone()[0]
    # no-qa: B608
    res = cur.execute(
        f"SELECT id, reset_token FROM {Auth.__tablename__} where user_id = ? AND active = 1",
        (user_id,),
    )
    return res.fetchone()


def test_password_reset(client: TestClient):
    response = client.post(
        "/user",
        json={"username": "test_user_creation", "email": "manoelhc@gmail.com"},
    )
    output = response.json()
    print(output)
    username = output["username"]
    token = get_activation_token(username)
    password = get_password_hash("Secret123#!")
    json = {
        "username": username,
        "reset_token": token,
        "new_password": password,
        "new_password_confirm": password,
    }

    response = client.patch("/auth/password", json=json)
    print(response.json())
    assert response.status_code == 200
