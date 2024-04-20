FROM python:3.12.3-slim-bookworm AS base_upgraded
# FROM python:3.12 as base

RUN apt update && apt upgrade -y

FROM base_upgraded AS base_pandoc
RUN apt install pandoc -y
RUN apt install texlive -y
RUN apt install texlive-latex-base -y
RUN apt install texlive-fonts-recommended -y
# RUN apt install texlive-extra-utils -y
# RUN apt install texlive-latex-extra -y
RUN apt update -y
RUN apt install texlive-xetex -y

FROM base_pandoc AS base
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base AS prod
COPY . .
