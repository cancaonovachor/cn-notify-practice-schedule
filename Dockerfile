FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONPATH="/app:$PYTHONPATH"

RUN apt-get update && apt-get install -y \
    build-essential \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY poetry.toml ./
COPY poetry.lock ./

RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev && rm -rf ~/.cache

# RUN poetry install --without dev

COPY . .
RUN chmod -R +x ./
ENV PYTHONPATH app

RUN ls -al

# Run script.py when the container launches
CMD ["poetry", "run", "python", "main.py", "--server.port", "8080"]