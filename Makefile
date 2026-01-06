.PHONY: setup install run-mock docker-build docker-run stop-mock run-engine verify clean

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn
PYTEST = $(VENV)/bin/pytest

setup:
	python3 -m venv $(VENV)

install: setup
	$(PIP) install -r requirements.txt

compose-up:
	docker-compose up -d axiom-ui

compose-test:
	docker-compose run --rm axiom-tests

up: compose-up

up-all:
	docker-compose up --build -d

down:
	docker-compose down

cleanup:
	docker-compose down --volumes --remove-orphans
	docker image prune -f

run-mock:
	@echo "Starting Mock Service..."
	$(UVICORN) src.mock_service.main:app --port 8000 --reload &
	sleep 2

docker-build:
	docker build -t axiom-app .

docker-run: docker-build
	docker run -p 8501:8501 -p 8000:8000 --env OPENAI_API_KEY=$(OPENAI_API_KEY) axiom-app

run-engine:
	@echo "Generating Tests..."
	$(PYTHON) src/engine/main.py docs/project_sample.md tests/generated_suite_test.py http://localhost:8000

verify: install stop-mock run-mock run-engine
	@echo "Running Verification..."
	$(PYTEST) tests/generated_suite_test.py || echo "Tests failed as expected (Intentional Bug)"
	$(MAKE) stop-mock

clean:
	rm -rf $(VENV)
	rm -f tests/generated_suite_test.py
