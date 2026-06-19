.PHONY: build check contract-test lint test verify

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= python3

lint:
	$(PYTHON) -m py_compile "$(ROOT)/comet_chat/application.py" "$(ROOT)/socket_chat/application.py"
	$(PYTHON) "$(ROOT)/scripts/check_docs_plans.py"

test:
	cd "$(ROOT)" && $(PYTHON) -m pytest -q

contract-test:
	$(PYTHON) "$(ROOT)/scripts/test_workflow_contract.py"
	$(PYTHON) "$(ROOT)/scripts/test_websocket_message_rate_contract.py"

build: lint

verify: lint contract-test test build

check: verify
	env -u PYTHONPATH $(PYTHON) -m pip check
	env -u PYTHONPATH $(PYTHON) -m pip_audit -r "$(ROOT)/requirements.txt"
