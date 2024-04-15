import datetime
import hashlib
import secrets
import socket
import docker
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG)
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

    def _docker_build(self) -> bool:
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
        image = self._client.images.build(
            path=self._context,
            tag=f"{self._image_name}:{self._tag}",
            dockerfile=self._dockerfile_path,
        )
        if image:
            return True
        return False

    def _docker_run(self) -> bool:
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
        env = {
            "HOST": "0.0.0.0",  # nosec: B104
        }
        container = self._client.containers
        result = container.run(
            f"{self._image_name}:{self._tag}",
            name=self._container_name,
            detach=True,
            environment=env,
            ports={self._port: self._port},
        )
        if result:
            return True
        logger.error("Error running the container.")
        return False

    def _docker_exec(self, cmd: list[str], envs: dict[str, str]) -> bool:
        container = self._client.containers.get(self._container_name)
        if container:
            result = container.exec_run(cmd=" ".join(cmd), environment=envs)
            if result and result.exit_code == 0:
                return True
            logger.error(
                "Error executing the command: Container %s, Command %s",
                container.name,
                cmd,
            )
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
            + "-".join([str(secrets.randbits(32)) for _ in range(10)])
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
        try:
            client = docker.from_env()
            container = client.containers.list(all=True, filters={"name": name})
            if container:
                return True
            image = client.images.list(filters={"reference": name})
            if image:
                return True
        except docker.errors.APIError as e:
            logger.error("Error checking if the object exists: %s", e)
        return False

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

        port = 5000
        while port in DockerContainerDaemon.ports or is_port_in_use(port):
            port = port + 1

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
        self._client = docker.from_env()
        """
        Initialize a DockerContainerDaemon object.

        Args:
            port (int, optional): The port number to expose on the container.
            image_name (str, optional): The name of the Docker image.
            tag (str, optional): The tag of the Docker image.
            context (str, optional): The build context for the Docker image.
            dockerfile_path (str, optional): The path to the Dockerfile.
        """
        self._dockerfile_path = dockerfile_path
        if tag == "":
            tag = DockerContainerDaemon.get_next_tag()
        self._tag = tag

        if image_name == "":
            image_name = "pytest_" + DockerContainerDaemon.get_next_image_name()
        self._image_name = image_name

        if port == 0:
            port = DockerContainerDaemon.get_next_port()
        self._port = str(port)

        self._context = context
        self._container_name = (
            "pytest_" + DockerContainerDaemon.get_next_container_name()
        )

    def build(self) -> bool:
        """
        Builds a Docker container using the specified Dockerfile and context.

        Returns:
            bool: True if the build was successful, False otherwise.
        """
        return self._docker_build()

    def start(self):
        """
        Start the Docker container.

        Returns:
            bool: True if the container is started successfully, False otherwise.
        """
        # Start the app.
        if not self.is_running():
            container = self._docker_run()
            if container:
                return self.is_running()
        return False

    def is_running(self) -> bool:
        """
        Check if the Docker container is running.

        Returns:
            bool: True if the container is running, False otherwise.
        """
        for i in range(1, 6):
            try:
                container = self._client.containers.get(self._container_name)
                if container and container.status == "running":
                    return True
            except docker.errors.NotFound:
                logger.error("Attempt #%s failed.", i)
            sleep(1)
        return False

    def get_port(self):
        """
        Get the port of the Docker container.

        Returns:
            int: The port of the container.
        """
        return self._port

    def run(self, cmd: list[str], env: dict[str, str] = None):
        """
        Executes a command within a Docker container.

        Args:
            cmd (list[str]): The command to be executed.
            env (dict[str, str], optional): Environment variables to be set for
                                            the command execution. Defaults to None.

        Returns:
            bool: True if the command execution is successful, False otherwise.
        """
        defaults = {
            "HOST": "0.0.0.0",  # nosec: B104
        }
        if env:
            env = defaults | env
        else:
            env = defaults
        try:
            return self._docker_exec(cmd, envs=env)
        except Exception as e:
            logger.error("Error running command: %s", e)
        return False

    def terminate(self) -> bool:
        """
        Terminate the Docker container.

        Returns:
            bool: True if the container is terminated successfully, False otherwise.
        """
        # Shutdown the app
        try:
            container = self._client.containers.get(self._container_name)
            if container:
                container.stop()
                return True
            return False
        except docker.errors.NotFound:
            return False

    def destroy(self) -> bool:
        self.terminate()
        try:
            container = self._client.containers.get(self._container_name)
            if container:
                container.remove()
                image = self._client.images.get(self._image_name)
                if image:
                    image.remove()
                    return True
        except docker.errors.NotFound:
            logger.debug("Container or image not found.")
        return False
