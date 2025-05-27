.PHONY: install run check format clean

install:
	pip install -r requirements.txt
	pip install -r dev-requirements.txt

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 10000

check:
	black --check .
	isort --check-only .
	mypy .

format:
	black .
	isort .

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +
