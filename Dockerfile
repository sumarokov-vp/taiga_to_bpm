FROM python:3.12.3-slim-bookworm AS base

RUN apt update && apt upgrade -y
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base AS prod
COPY . .
