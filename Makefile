.PHONY: build check lint test verify

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile "$(ROOT)/comet_chat/application.py" "$(ROOT)/socket_chat/application.py"
	$(PYTHON) "$(ROOT)/scripts/check_docs_plans.py"

test:
	cd "$(ROOT)" && $(PYTHON) -m pytest -q

build: lint

verify: lint test build

check: verify
	env -u PYTHONPATH $(PYTHON) -m pip check
	env -u PYTHONPATH $(PYTHON) -m pip_audit -r "$(ROOT)/requirements.txt"
