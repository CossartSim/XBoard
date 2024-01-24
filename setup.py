from setuptools import setup, find_packages

with open("README.md", "r") as file:
    description = file.read()

setup(
    name = "xboard",
    version = "0.0.0",
    packages = find_packages(),
    install_requires = [
        # dependences
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)