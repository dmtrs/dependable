FROM python:3.9-slim-buster

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python
RUN ln -s /opt/poetry/bin/poetry /usr/local/bin/. \
  && chmod o+x /opt/poetry/bin/poetry

RUN useradd -ms /bin/bash user
USER user

# RUN poetry config virtualenvs.create false

WORKDIR /usr/src/app/

COPY ./pyproject.toml  .
RUN poetry install --no-root # --no-dev
