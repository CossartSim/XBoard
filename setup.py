from setuptools import setup, find_packages


with open("README.md", "r") as file:
    description = file.read()

setup(
    name = "xboard",
    version = "1.0.3",
    description = "API for the XBoard hangboard",
    url = "https://github.com/CossartSim/XBoard",
    packages = find_packages(),
    install_requires=[
        "sseclient>=0.0.20",
    ],
)