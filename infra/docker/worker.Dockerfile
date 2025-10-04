FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/ai.txt requirements/worker.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir -r requirements/ai.txt && \
    pip install --no-cache-dir -r requirements/worker.txt

COPY pyproject.toml ./
COPY services ./services
COPY packages ./packages
COPY configs ./configs

RUN pip install --no-cache-dir -e packages/common

ENV PYTHONPATH="/app"

CMD ["celery", "-A", "services.worker.src.celery_app:celery_app", "worker", "-l", "info"]
