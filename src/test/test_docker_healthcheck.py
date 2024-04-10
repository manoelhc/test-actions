from time import sleep
import pytest
import config
import subprocess
import datetime
import hashlib
import random
from docker_healthcheck import check_health


class DockerContainerDaemon:
    # Test the app class.
    pid: int = -1
    container_name: str = ""
    image_name: str = ""
    tag: str = ""
    port: str = str(config.PORT)
    context: str = ""
    dockerfile_path: str = ""
    proc = None

    def build(
        self,
        port: int = config.PORT,
        image_name: str = "",
        tag: str = "",
        context: str = ".",
        dockerfile_path: str = "./Dockerfile",
    ) -> bool:
        # Build the app.
        # Container name is the sha256 hash of the image name, tag and datetime.now().
        self.dockerfile_path = dockerfile_path
        salt = (
            str(datetime.datetime.now())
            + str(random.randint(0, 100000))
            + str(random.randint(0, 100000))
            + str(datetime.datetime.now())
        )

        if tag == "":
            tag = hashlib.sha256(f"test-tag:{salt}".encode()).hexdigest()[:10]

        self.tag = tag
        if image_name == "":
            image_name = hashlib.sha256(
                f"test-image:{self.tag}{salt}".encode(),
            ).hexdigest()[:15]
        self.image_name = image_name
        self.port = str(port)
        self.context = context
        self.container_name = hashlib.sha256(
            f"{image_name}:{tag}:{salt}".encode(),
        ).hexdigest()[:15]
        proc = subprocess.run(
            [
                "docker",
                "build",
                "-t",
                f"{image_name}:{tag}",
                "-f",
                dockerfile_path,
                context,
            ],
        )
        return proc.returncode == 0

    def start(self):
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
            self.service = subprocess.Popen(cmd)

            if self.service.returncode != 0:
                return False
            self.pid = self.service.pid
            return True
        return False

    def is_running(self):
        # Check if the app is running.
        if self.container_name == "" or self.pid == -1:
            return False
        proc = subprocess.run(["docker", "inspect", self.container_name])
        return proc.returncode == 0

    def run(self, cmd: list[str]):
        docker_exec = ["docker", "exec", self.container_name] + cmd
        print(docker_exec)
        run = subprocess.run(docker_exec)
        return run.returncode == 0

    def terminate(self):
        """Shutdown the app."""
        self.service.terminate()
        run = subprocess.run(["docker", "stop", "container", self.container_name])
        return run.returncode == 0

    def destroy(self):
        """Destroy the app."""
        run = subprocess.run(["docker", "rm", self.container_name])
        if run.returncode == 0:
            run = subprocess.run(["docker", "rmi", f"{self.image_name}:{self.tag}"])
            return run.returncode == 0


@pytest.fixture
def docker_session():
    # Setup the test app.
    ds = DockerContainerDaemon()
    ds.build()
    ds.start()
    # Create a better way to wait for the app to start by checking if it passed the Docker healthcheck.
    sleep(10)
    yield ds
    ds.terminate()
    ds.destroy()


def test_check_health(docker_session):
    # Test the check_health function.
    assert check_health()


def test_check_health_calling_the_file(docker_session):
    # Test the check_health function via running the file.
    assert docker_session.run(["python", "docker_healthcheck.py"])


def test_check_invalid_file(docker_session):
    # Test if docker exec fails when running an invalid file to avoid false positives.
    assert not docker_session.run(["python", "invalid_file.py"])


def test_check_health_calling_the_module(docker_session):
    # Test the check_health function via running the module.
    assert docker_session.run(["python", "-m", "docker_healthcheck"])
