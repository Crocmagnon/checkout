FROM mcr.microsoft.com/devcontainers/python:3.13-bookworm
RUN apt-get update && apt-get upgrade -y
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock tasks.py ./
RUN uv sync --frozen
