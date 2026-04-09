.PHONY: dev db migrate test lint

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db:
	docker compose up -d db

db-stop:
	docker compose down

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"

test:
	pytest -v

lint:
	ruff check app/ tests/
	ruff format --check app/ tests/

format:
	ruff format app/ tests/

install:
	pip install -e ".[dev]"
