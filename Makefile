.PHONY: lint test build verify

PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile comet_chat/application.py socket_chat/application.py

test:
	$(PYTHON) -m pytest -q

build: lint

verify: lint test build
