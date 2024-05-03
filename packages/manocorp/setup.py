# Setup file to install the DockerContainerDaemon class.
import os
from setuptools import setup


def read(fname):
    """    Read the contents of a file.

    Args:
        fname (str): The name of the file to be read.

    Returns:
        str: The contents of the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """

    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="manocorp",
    version="0.0.1",
    packages=[
        "manocorp",
        "manocorp.fastapi.routing",
        "manocorp.testing",
    ],
    install_requires=["fastapi>=0.110.1"],
    license="MIT",
    author="Manoel Carvalho",
    description="Manocorp Utils package.",
    long_description=read("README.md"),
)
