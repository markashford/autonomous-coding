PYTHON ?= python3

.PHONY: install install-dev test test-legacy run docker-build docker-run

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest

test-legacy:
	$(PYTHON) test_security.py

run:
	$(PYTHON) autonomous_agent_demo.py --project-dir autonomous_demo_project --max-iterations 1

docker-build:
	docker compose build

docker-run:
	docker compose run --rm autonomous-agent
