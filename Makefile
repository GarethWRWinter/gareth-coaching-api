install:
	pip install -r requirements.txt
	pip install -r dev-requirements.txt

check:
	mypy .

run:
	uvicorn main:app --reload --host 0.0.0.0 --port 10000
