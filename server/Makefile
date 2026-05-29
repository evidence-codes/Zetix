# server — FastAPI service (api) + embedding service. Phase 1 / EPIC-1.
# Native tool: Python toolchain (pip/uv, pytest, ruff) + Docker Compose.
# The root Makefile delegates `make server-*` here.
.PHONY: build test lint fmt up down bootstrap clean

# Prefer the project venv if present, else the ambient python (e.g. CI).
VENV := .venv
PY := $(if $(wildcard $(VENV)/bin/python),$(VENV)/bin/python,python3)

bootstrap:  ## Create a local venv and install dev deps
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install -U pip
	$(VENV)/bin/python -m pip install -e ".[dev]"

build:  ## Install the package + dev/test deps
	$(PY) -m pip install -e ".[dev]"

test:  ## Run the test suite
	$(PY) -m pytest -q

lint:  ## Lint
	$(PY) -m ruff check .

fmt:  ## Auto-format
	$(PY) -m ruff format .

up:  ## Start API + Postgres (background)
	docker compose up -d --build

down:  ## Stop the stack
	docker compose down

clean:  ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache build dist **/*.egg-info
