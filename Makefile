.PHONY: build check lint test verify

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile comet_chat/application.py socket_chat/application.py
	$(PYTHON) scripts/check_docs_plans.py

test:
	$(PYTHON) -m pytest -q

build: lint

verify: lint test build

check: verify
	$(PYTHON) -m pip_audit --local
