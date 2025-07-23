FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./


RUN uv sync --frozen --no-cache


COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

