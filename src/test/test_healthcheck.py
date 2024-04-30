from fastapi.testclient import TestClient
from migrations import create_db_and_tables, delete_db_and_tables
from app import app
import pytest


@pytest.fixture
def client():
    """    Function to set up and tear down database and tables for testing purposes using a test client.

    It first creates the necessary database and tables, then initializes a test client for the application.
    After the test client is used, it tears down the database and tables and closes the client.

    Yields:
        TestClient: A test client for the application.
    """

    create_db_and_tables()
    client = TestClient(app)
    yield client
    delete_db_and_tables()
    client.close()


def test_healthcheck(client: TestClient):
    """    Perform a health check on the client.

    This function sends a GET request to the "/health" endpoint of the client and checks the response for a status code of 200 and a JSON object containing a "status" key with the value "ok".

    Args:
        client (TestClient): The client to perform the health check on.

    Raises:
        AssertionError: If the response status code is not 200 or if the "status" key is not present in the response JSON or if its value is not "ok".
    """

    response = client.get("/health")
    assert response.status_code == 200
    output = response.json()
    assert "status" in output
    assert output["status"] == "ok"
