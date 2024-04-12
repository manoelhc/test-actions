from fastapi.testclient import TestClient
from migrations import create_db_and_tables, delete_db_and_tables
from app import app
import pytest


@pytest.fixture
def client():
    create_db_and_tables()
    client = TestClient(app)
    yield client
    delete_db_and_tables()
    client.close()


def test_healthcheck(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    output = response.json()
    assert "status" in output
    assert output["status"] == "ok"
