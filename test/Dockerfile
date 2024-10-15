FROM python:alpine3.20

RUN apk update && apk add bash

RUN python3 -m pip install coverage

# Suppresses the __pycache__ folders
ENV PYTHONDONTWRITEBYTECODE=1