from time import sleep
import pytest
import subprocess
import datetime
import hashlib
import random
from docker_healthcheck import check_health
import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DockerContainerDaemon:
    """
    A class representing a Docker container daemon.

    Attributes:
        ports (list): A list of ports used by the Docker containers.
        image_names (list): A list of image names used by the Docker containers.
        tags (list): A list of tags used by the Docker containers.
        container_names (list): A list of container names used by the
                                Docker containers.
    """

    ports = []
    image_names = []
    tags = []
    container_names = []

    @staticmethod
    def system_call(cmd: list[str], timeout=10) -> bool:
        """
        Execute a system command.

        Args:
            cmd (list): The command to be executed.
            timeout (int): The timeout for the command execution
                           (default is 5 seconds).
            envs (dict): Additional environment variables for the command execution
                         (default is an empty dictionary).

        Returns:
            bool: True if the command execution is successful, False otherwise.
        """
        tmp = " ".join(cmd)
        print(f"Running command: {tmp}")
        try:
            subprocess.run(cmd, check=True, timeout=timeout)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_hash():
        """
        Generate a random hash.

        Returns:
            str: The generated hash.
        """
        rands = (
            "DCD"
            + "-".join([str(random.randint(0, 1000)) for _ in range(10)])
            + str(datetime.datetime.now())
        )
        return hashlib.sha256(rands.encode()).hexdigest()[:15]

    @staticmethod
    def check_if_object_exists(name: str) -> bool:
        """
        Check if a Docker object exists.

        Args:
            name (str): The name of the Docker object.

        Returns:
            bool: True if the Docker object exists, False otherwise.
        """
        return DockerContainerDaemon.system_call(["docker", "inspect", name])

    @staticmethod
    def get_next_port():
        """
        Get the next available port.

        Returns:
            int: The next available port.
        """

        def is_port_in_use(port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", port)) == 0

        port = random.randint(5000, 8000)

        while port in DockerContainerDaemon.ports or is_port_in_use(port):
            port = random.randint(5000, 6000)

        DockerContainerDaemon.ports.append(port)
        return port

    @staticmethod
    def get_next_image_name():
        """
        Get the next available image name.

        Returns:
            str: The next available image name.
        """
        image_name = DockerContainerDaemon.get_hash()
        while (
            image_name in DockerContainerDaemon.image_names
            or DockerContainerDaemon.check_if_object_exists(image_name)
        ):
            image_name = DockerContainerDaemon.get_hash()

        DockerContainerDaemon.image_names.append(image_name)
        return image_name

    @staticmethod
    def get_next_tag():
        """
        Get the next available tag.

        Returns:
            str: The next available tag.
        """
        tag = DockerContainerDaemon.get_hash()
        while tag in DockerContainerDaemon.tags:
            tag = DockerContainerDaemon.get_hash()
        DockerContainerDaemon.tags.append(tag)
        return tag

    @staticmethod
    def get_next_container_name():
        """
        Get the next available container name.

        Returns:
            str: The next available container name.
        """
        container_name = DockerContainerDaemon.get_hash()
        while container_name in DockerContainerDaemon.container_names:
            container_name = DockerContainerDaemon.get_hash()
        DockerContainerDaemon.container_names.append(container_name)
        return container_name

    def __init__(
        self,
        port: int = 0,
        image_name: str = "",
        tag: str = "",
        context: str = ".",
        dockerfile_path: str = "./Dockerfile",
    ) -> None:
        """
        Initialize a DockerContainerDaemon object.

        Args:
            port (int, optional): The port number to expose on the container. Defaults to 0.
            image_name (str, optional): The name of the Docker image. Defaults to an empty string.
            tag (str, optional): The tag of the Docker image. Defaults to an empty string.
            context (str, optional): The build context for the Docker image. Defaults to ".".
            dockerfile_path (str, optional): The path to the Dockerfile. Defaults to "./Dockerfile".
        """
        self.dockerfile_path = dockerfile_path
        if tag == "":
            tag = DockerContainerDaemon.get_next_tag()
        self.tag = tag

        if image_name == "":
            image_name = DockerContainerDaemon.get_next_image_name()
        self.image_name = image_name

        if port == 0:
            port = DockerContainerDaemon.get_next_port()
        self.port = str(port)

        self.context = context
        self.container_name = DockerContainerDaemon.get_next_container_name()

    def build(self) -> bool:
        """
        Builds a Docker container using the specified Dockerfile and context.

        Returns:
            bool: True if the build was successful, False otherwise.
        """
        return DockerContainerDaemon.system_call(
            [
                "docker",
                "build",
                "-t",
                f"{self.image_name}:{self.tag}",
                "-f",
                self.dockerfile_path,
                self.context,
            ],
            timeout=300,
        )

    def start(self):
        """
        Start the Docker container.

        Returns:
            bool: True if the container is started successfully, False otherwise.
        """
        # Start the app.
        if not self.is_running():
            cmd = [
                "docker",
                "run",
                "-d",
                "-e",
                f"PORT={self.port}",
                "-e",
                "HOST=0.0.0.0",
                "-p",
                f"{self.port}:{self.port}",
                "--name",
                self.container_name,
                f"{self.image_name}:{self.tag}",
            ]
            if DockerContainerDaemon.system_call(cmd):
                retry = 0
                max_retries = 2
                while not self.is_running():
                    if retry == max_retries:
                        return False
                    sleep(1)
                    retry = retry + 1
                return True
        return False

    def is_running(self) -> bool:
        """
        Check if the Docker container is running.

        Returns:
            bool: True if the container is running, False otherwise.
        """
        # Check if the app is running.
        if self.container_name == "":
            return False
        res = DockerContainerDaemon.system_call(
            ["docker", "inspect", self.container_name],
            timeout=10,
        )
        print(f"Container {self.container_name} is running?: {res}")
        return res

    def get_port(self):
        """
        Get the port of the Docker container.

        Returns:
            int: The port of the container.
        """
        return self.port

    def run(self, cmd: list[str], env: dict[str, str] = None):
        """
        Run a command inside the Docker container.

        Args:
            cmd (list): The command to be executed inside the container.
            env (dict): Additional environment variables for the command
                        execution (default is an empty dictionary).

        Returns:
            bool: True if the command execution is successful, False otherwise.
        """
        envs = ["-e", f"PORT={self.get_port()}"]
        if env is not None:
            for key, value in env.items():
                envs.append("-e")
                envs.append(f"{key}={value}")

        full_cmd = ["docker", "exec", *envs, self.container_name] + cmd
        return DockerContainerDaemon.system_call(full_cmd)

    def terminate(self) -> bool:
        """
        Terminate the Docker container.

        Returns:
            bool: True if the container is terminated successfully, False otherwise.
        """
        # Shutdown the app
        return DockerContainerDaemon.system_call(
            ["docker", "stop", self.container_name],
        )

    def destroy(self) -> bool:
        """
        Destroy the Docker container.

        Returns:
            bool: True if the container is destroyed successfully, False otherwise.
        """
        # Destroy the container and image.
        return DockerContainerDaemon.system_call(
            ["docker", "rm", self.container_name],
        ) and DockerContainerDaemon.system_call(
            ["docker", "rmi", f"{self.image_name}:{self.tag}", "-f"],
        )


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
    assert check_health(docker_session.get_port())


def test_check_invalid_port_endpoint(docker_session: DockerContainerDaemon):
    """
    Test case for checking an invalid health endpoint (Port).

    Args:
        docker_session (DockerContainerDaemon): The Docker container
                                                daemon session.

    Returns:
        None
    """
    assert not check_health("8088")


def test_check_invalid_host_endpoint(docker_session: DockerContainerDaemon):
    """
    Test case for checking an invalid health endpoint (Hostname).

    Args:
        docker_session (DockerContainerDaemon): The Docker container
        daemon session.

    Returns:
        None
    """
    assert not docker_session.run(
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
    assert not check_health(docker_session.get_port(), "/invalid_endpoint")


def test_check_invalid_health_endpoint(docker_session: DockerContainerDaemon):
    """
    Test case for checking an invalid health endpoint.

    Args:
        docker_session (DockerContainerDaemon): The Docker container
        daemon session.

    Returns:
        None
    """
    assert not check_health("8088")


def test_check_health_calling_the_file(docker_session: DockerContainerDaemon):
    """
    Test the check_health function by running the file.

    Args:
        docker_session (DockerContainerDaemon): The Docker container session.

    Returns:
        None
    """
    assert docker_session.run(["python", "docker_healthcheck.py"])


def test_check_invalid_file(docker_session: DockerContainerDaemon):
    """
    Test if docker exec fails when running an invalid file to avoid false positives.

    Args:
        docker_session (DockerContainerDaemon): The Docker container session to
        run the test on.

    """
    assert not docker_session.run(["python", "invalid_file.py"])


def test_check_health_calling_the_module(docker_session: DockerContainerDaemon):
    """
    Test the check_health function by running the module.

    Args:
        docker_session (DockerContainerDaemon): The Docker container session.

    Returns:
        None
    """
    assert docker_session.run(["python", "-m", "docker_healthcheck"])
