from fastapi.testclient import TestClient
from migrations import create_db_and_tables, delete_db_and_tables, engine
from app import app
from helpers.auth import password_generator
from helpers.jwt import decode_jwt_token
import pytest
import config
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
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()

    username = output["username"]
    token = get_activation_token(username)
    password = password_generator()
    json = {
        "username": username,
        "reset_token": token[1],
        "new_password": password,
        "new_password_confirm": password,
    }

    response = client.patch("/auth/password", json=json)
    print(response.json())
    assert response.status_code == 200


def test_failed_password_reset_wrong_password_confirm(client: TestClient):
    response = client.post(
        "/user",
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()
    username = output["username"]
    token = get_activation_token(username)
    password = password_generator()
    json = {
        "username": username,
        "reset_token": token[1],
        "new_password": password,
        "new_password_confirm": "wrong_password",
    }
    response = client.patch("/auth/password", json=json)
    assert response.status_code == 400


def test_failed_password_weak_password(client: TestClient):
    response = client.post(
        "/user",
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()
    username = output["username"]
    token = get_activation_token(username)
    password = password_generator()[:4]
    json = {
        "username": username,
        "reset_token": token[1],
        "new_password": password,
        "new_password_confirm": password,
    }
    response = client.patch("/auth/password", json=json)
    assert response.status_code == 400


def test_failed_password_wrong_token(client: TestClient):
    response = client.post(
        "/user",
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()
    username = output["username"]
    token = get_activation_token(username)
    password = password_generator()
    json = {
        "username": username,
        "reset_token": token[1][:10],
        "new_password": password,
        "new_password_confirm": password,
    }
    response = client.patch("/auth/password", json=json)
    assert response.status_code == 400


def test_failed_wrong_user_password_reset(client: TestClient):
    response = client.post(
        "/user",
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()
    username = output["username"]
    token = get_activation_token(username)
    username = output["username"] + "wrong"
    password = password_generator()
    json = {
        "username": username,
        "reset_token": token[1],
        "new_password": password,
        "new_password_confirm": password,
    }
    response = client.patch("/auth/password", json=json)
    assert response.status_code == 400


def test_login(client: TestClient):
    response = client.post(
        "/user",
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()
    username = output["username"]
    token = get_activation_token(username)
    password = password_generator()
    json = {
        "username": username,
        "reset_token": token[1],
        "new_password": password,
        "new_password_confirm": password,
    }
    client.patch("/auth/password", json=json)
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    output = response.json()
    print(output)

    assert response.status_code == 200
    assert "access_token" in output

    token = decode_jwt_token(output["access_token"])
    assert token["username"] == username


def test_faled_login(client: TestClient):
    response = client.post(
        "/user",
        json={"username": config.TEST_USERNAME, "email": config.TEST_USEREMAIL},
    )
    output = response.json()
    username = output["username"]
    token = get_activation_token(username)
    password = password_generator()
    json = {
        "username": username,
        "reset_token": token[1],
        "new_password": password,
        "new_password_confirm": password,
    }
    client.patch("/auth/password", json=json)
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password + "wrong"},
    )
    output = response.json()
    print(output)

    assert response.status_code == 422
