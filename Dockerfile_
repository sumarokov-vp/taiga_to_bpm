FROM python:3.12 AS base

# Use poetry without virtualenv
ENV POETRY_HOME=/opt/poetry
ENV POETRY_CACHE_DIR=/opt/.cache
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$PATH:$POETRY_HOME/bin"

# Install poetry
RUN apt update && apt upgrade -y
RUN curl -sSL https://install.python-poetry.org | python3.12 -
RUN mkdir /app
WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install

FROM base AS prod
COPY . .
