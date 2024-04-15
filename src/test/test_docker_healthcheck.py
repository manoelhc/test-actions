import pytest
from docker_healthcheck import check_health
from manocorp.testing import DockerContainerDaemon


@pytest.fixture
def docker_session():
    # Setup the test app.
    ds = DockerContainerDaemon()
    ds.build()
    ds.start()
    yield ds
    ds.terminate()
    ds.destroy()


def test_check_health(docker_session: DockerContainerDaemon):
    """
    Test the check_health function.

    Args:
        docker_session: An instance of DockerContainerDaemon
                        representing the Docker container session.

    Returns:
        None
    """
    assert check_health(docker_session.get_port())  # nosec: B101


def test_check_invalid_port_endpoint(docker_session: DockerContainerDaemon):
    """
    Test case for checking an invalid health endpoint (Port).

    Args:
        docker_session (DockerContainerDaemon): The Docker container
                                                daemon session.

    Returns:
        None
    """
    assert not check_health("8088")  # nosec: B101


def test_check_invalid_host_endpoint(docker_session: DockerContainerDaemon):
    """
    Test case for checking an invalid health endpoint (Hostname).

    Args:
        docker_session (DockerContainerDaemon): The Docker container
        daemon session.

    Returns:
        None
    """
    assert not docker_session.run(  # nosec: B101
        ["python", "docker_healthcheck.py"],
        {"HOST": "whatever_host"},
    )


def test_check_invalid_path_endpoint(docker_session: DockerContainerDaemon):
    """
    Test case for checking an invalid health endpoint (Endpoint).

    Args:
        docker_session (DockerContainerDaemon): The Docker container
        daemon session.

    Returns:
        None
    """
    assert not check_health(docker_session.get_port(), "/invalid_endpoint")  # nosec: B101


def test_check_health_calling_the_file(docker_session: DockerContainerDaemon):
    """
    Test the check_health function by running the file.

    Args:
        docker_session (DockerContainerDaemon): The Docker container session.

    Returns:
        None
    """
    assert docker_session.run(["python", "docker_healthcheck.py"])  # nosec: B101


def test_check_invalid_file(docker_session: DockerContainerDaemon):
    """
    Test if docker exec fails when running an invalid file to avoid false positives.

    Args:
        docker_session (DockerContainerDaemon): The Docker container session to
        run the test on.

    """
    assert not docker_session.run(["python", "invalid_file.py"])  # nosec: B101


def test_check_health_calling_the_module(docker_session: DockerContainerDaemon):
    """
    Test the check_health function by running the module.

    Args:
        docker_session (DockerContainerDaemon): The Docker container session.

    Returns:
        None
    """
    assert docker_session.run(["python", "-m", "docker_healthcheck"])  # nosec: B101
