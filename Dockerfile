FROM python:2.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip

RUN pip install -r requirements-dev.txt

