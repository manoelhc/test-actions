from fastapi.testclient import TestClient
from migrations import create_db_and_tables, delete_db_and_tables, seed_db
from app import app
import pytest


@pytest.fixture
def client():
    create_db_and_tables()
    seed_db()
    client = TestClient(app)
    yield client
    delete_db_and_tables()
    client.close()


def test_create_user(client: TestClient):
    # Test new user creation
    response = client.post("/user", json={"username": "test321"})
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output


def test_invalid_users(client: TestClient):
    response = client.post("/user", json={"username": "t"})
    assert response.status_code == 422

    response = client.post("/user", json={"username": "ttt&"})
    assert response.status_code == 422

    response = client.post("/user", json={"username": "ttt.asd"})
    assert response.status_code == 422

    response = client.post("/user", json={"username": "ttt-test"})
    assert response.status_code == 422

    response = client.post("/user", json={"username": "tt*"})
    assert response.status_code == 422

    response = client.post("/user", json={"username": "laws[deleted]"})
    assert response.status_code == 422


def test_duplicate_user(client: TestClient):
    # Test duplicate user creation
    response = client.post("/user", json={"username": "test321"})
    assert response.status_code == 200
    response = client.post("/user", json={"username": "test321"})
    assert response.status_code == 400
    output = response.json()
    assert "detail" in output


def test_user_not_found(client: TestClient):
    # Test invalid username
    response = client.get("/user/terminator")
    assert response.status_code == 404
    output = response.json()
    assert "detail" in output


def test_read_user(client: TestClient):
    response = client.post("/user", json={"username": "test321"})
    assert response.status_code == 200
    # Test user found
    response = client.get("/user/test321")
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output


def test_read_user_not_found(client: TestClient):
    # Test user not found
    response = client.get("/user/txyz")
    assert response.status_code == 404
    output = response.json()
    assert "detail" in output


def test_enabling_disabling_user(client: TestClient):
    response = client.post("/user", json={"username": "test321"})
    assert response.status_code == 200
    # Get user id
    user_id = client.get("/user/test321").json()["id"]

    # Set user to inactive
    response = client.put(
        "/user/",
        json={"username": "test321", "id": user_id, "is_active": False},
    )
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output

    # Test user not found
    response = client.get("/user/test321")
    assert response.status_code == 404
    output = response.json()
    assert "detail" in output

    # Set user to active
    response = client.put(
        "/user/",
        json={"username": "test321", "id": user_id, "is_active": True},
    )
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output

    # Test user found
    response = client.get("/user/test321")
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output


def test_changing_user_name(client: TestClient):
    # Create the "old" user
    response = client.post("/user", json={"username": "test321"})
    assert response.status_code == 200

    # Test new user creation
    response = client.post("/user", json={"username": "test123"})
    assert response.status_code == 200

    # Get user id
    old_user = client.get("/user/test321").json()

    # Set rename old user with an existing username
    response = client.put(
        "/user/",
        json={"username": "test123", "id": old_user["id"], "is_active": True},
    )
    assert response.status_code == 400
    output = response.json()
    assert "detail" in output

    # Set rename old user with an invalid username
    response = client.put(
        "/user/",
        json={"username": "t", "id": old_user["id"], "is_active": True},
    )
    assert response.status_code == 422
    output = response.json()
    assert "detail" in output

    # Set rename old user with an existing username
    response = client.put(
        "/user/",
        json={"username": "test1234", "id": old_user["id"], "is_active": True},
    )
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output

    # Test user found
    response = client.get("/user/test1234")
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output

    # Test user not found
    response = client.get("/user/test321")
    assert response.status_code == 404
    output = response.json()
    assert "detail" in output

    # Rename user back
    response = client.put(
        "/user/",
        json={"username": "test321", "id": old_user["id"], "is_active": True},
    )
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output

    # Test user not found
    response = client.get("/user/test321")
    assert response.status_code == 200
    output = response.json()
    assert "username" in output
    assert "created_at" in output
    assert "is_active" in output
    assert "updated_at" in output

    # Test user found
    response = client.get("/user/test1234")
    assert response.status_code == 404
    output = response.json()
    assert "detail" in output


def test_delete_users(client: TestClient):
    response = client.delete("/user/demo")
    assert response.status_code == 200
    for i in range(1, 31):
        user_number = str(i).rjust(3, "0")
        response = client.post("/user", json={"username": f"test_read_{user_number}"})
        assert response.status_code == 200
    response = client.get("/users/1")
    output = response.json()
    for user in output:
        response = client.delete(f"/user/{user['username']}")
        assert response.status_code == 200
        response = client.get(f"/user/{user['username']}")
        assert response.status_code == 404
        response = client.get(f"/user/{user['username']}[deleted]")
        assert response.status_code == 404


def test_read_all_users(client: TestClient):
    response = client.delete("/user/demo")
    assert response.status_code == 200

    # Generate 50 users
    for i in range(1, 31):
        user_number = str(i).rjust(3, "0")
        response = client.post("/user", json={"username": f"1_{user_number}"})
        assert response.status_code == 200

    # Test all users
    response = client.get("/users/1")
    output = response.json()
    assert len(output) == 20
    assert output[0]["username"] == "1_001"
    assert output[19]["username"] == "1_020"

    response = client.get("/users/2")
    output = response.json()
    assert len(output) == 10
    assert output[0]["username"] == "1_021"
    assert output[9]["username"] == "1_030"

    response = client.get("/users/3")
    output = response.json()
    assert len(output) == 0
    assert response.status_code == 200

    # Delete all users
    for i in range(1, 31):
        user_number = str(i).rjust(3, "0")
        response = client.delete(f"/user/1_{user_number}")
        assert response.status_code == 200

    # List all users (should be empty)
    response = client.get("/users/1")
    output = response.json()
    assert len(output) == 0
    assert response.status_code == 200
