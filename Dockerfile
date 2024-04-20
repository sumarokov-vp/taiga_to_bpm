FROM python:3.12.3-slim-bookworm

RUN apt update && apt upgrade -y
RUN apt install pandoc -y
RUN apt install texlive -y
RUN apt install texlive-latex-base -y
RUN apt install texlive-fonts-recommended -y
RUN apt update -y
RUN apt install texlive-xetex -y
RUN mkdir /app
WORKDIR /app
COPY requirements_base.txt .
RUN pip install -r requirements_base.txt
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
