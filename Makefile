.DEFAULT_GOAL := help

PYTHON ?= python3

help:
	@echo "Available commands:"
	@echo "  make install        Install base dependencies"
	@echo "  make install-all    Install all dependencies"
	@echo "  make dev            Run local dev stack"
	@echo "  make lint           Run ruff + black --check"
	@echo "  make format         Run black"
	@echo "  make test           Run pytest"
	@echo "  make seed           Run data seed script"

install:
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements/base.txt
	pip install -e packages/common

install-all:
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements/all.txt
	pip install -e packages/common

lint:
	ruff check services packages
	black --check services packages

format:
	black services packages

TEST_ENV ?= .env.test

test:
	pytest

dev:
	docker compose -f infra/docker/docker-compose.dev.yml up --build

seed:
	PYTHONPATH=. $(PYTHON) services/api/src/cli/seed_data.py
