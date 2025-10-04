FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/ai.txt requirements/worker.txt requirements/dev.txt requirements/all.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir -r requirements/ai.txt

COPY pyproject.toml ./
COPY services ./services
COPY packages ./packages
COPY configs ./configs

RUN pip install --no-cache-dir -e packages/common

ENV PYTHONPATH="/app"

CMD ["uvicorn", "services.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
