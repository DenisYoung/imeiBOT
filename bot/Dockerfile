# syntax=docker/dockerfile:experimental

FROM python:3.10-slim AS base

COPY BOTrequirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt


COPY . /app

WORKDIR /app


CMD ["python", "mainbot.py"]
