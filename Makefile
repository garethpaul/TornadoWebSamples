.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check contract-test lint root-test test verify
.SECONDEXPANSION:

PUBLIC_TARGETS := build check contract-test lint root-test test verify

PYTHON ?= python3
override PYTHON := $(value PYTHON)
export PYTHON
override REPOSITORY_MAKE_DOLLAR := $$
override REPOSITORY_MAKE_OPEN := (
ifneq ($(findstring $(REPOSITORY_MAKE_DOLLAR)$(REPOSITORY_MAKE_OPEN),$(value PYTHON)),)
$(error PYTHON must be a literal executable path, not Make syntax)
endif
override SHELL := /bin/sh
override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override REPOSITORY_SED := $(shell if [ -x /usr/bin/sed ]; then /usr/bin/printf '%s' /usr/bin/sed; elif [ -x /bin/sed ]; then /usr/bin/printf '%s' /bin/sed; fi)
override REPOSITORY_ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | '$(REPOSITORY_SED)' 's/^ //'); [ -f "$$path" ] || exit 1; directory=$${path%/*}; [ "$$directory" != "$$path" ] || directory=.; CDPATH= cd -- "$$directory" && /bin/pwd -P)
override ROOT := $(REPOSITORY_ROOT)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif

$(PUBLIC_TARGETS): override SHELL := /bin/sh
$(PUBLIC_TARGETS): override .SHELLFLAGS := -c
$(PUBLIC_TARGETS): override ROOT := $(REPOSITORY_ROOT)
$(PUBLIC_TARGETS): override PYTHON := $(value PYTHON)

$(PUBLIC_TARGETS):: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
$(PUBLIC_TARGETS):: $$(if $$(shell path=$$$$(/usr/bin/printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | '$$(REPOSITORY_SED)' 's/^ //') && [ -f "$$$$path" ] && /usr/bin/printf '%s' ok),,$$(error repository Makefile must be loaded alone))
$(PUBLIC_TARGETS):: __repository-make-authority

__repository-make-authority::
	@:

lint::
	"$$PYTHON" -I -B -m py_compile "$$ROOT/comet_chat/application.py" "$$ROOT/socket_chat/application.py"
	"$$PYTHON" -I -B "$$ROOT/scripts/check_docs_plans.py"

test::
	cd "$$ROOT" && "$$PYTHON" -I -B -m pytest -q

contract-test::
	"$$PYTHON" -I -B "$$ROOT/scripts/test_dependency_audit_contract.py"
	"$$PYTHON" -I -B "$$ROOT/scripts/test_workflow_contract.py"
	"$$PYTHON" -I -B "$$ROOT/scripts/test_websocket_message_rate_contract.py"

build:: lint

root-test::
	/bin/sh "$$ROOT/scripts/test-makefile-root.sh"

verify:: root-test lint contract-test test build

check:: verify
	env -u PYTHONPATH "$$PYTHON" -I -B "$$ROOT/scripts/check_runtime_deps.py"
	env -u PYTHONPATH "$$PYTHON" -I -B -m pip_audit -r "$$ROOT/requirements.txt"
	env -u PYTHONPATH "$$PYTHON" -I -B -m pip_audit -r "$$ROOT/test-requirements.txt"
