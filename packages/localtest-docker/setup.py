# Setup file to install the DockerContainerDaemon class.
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="localtest_docker",
    version="0.1.2",
    packages=["localtest_docker"],
    install_requires=["docker==7.0.0"],
    license="MIT",
    author="Manoel Carvalho",
    description="A package to test Docker containers.",
    long_description=read("README.md"),
)
