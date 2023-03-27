FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye
RUN apt-get update && apt-get upgrade -y
RUN pip install pip-tools invoke
COPY requirements.in requirements.txt requirements-dev.in requirements-dev.txt constraints.txt tasks.py ./
RUN invoke sync-dependencies
