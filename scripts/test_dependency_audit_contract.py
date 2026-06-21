#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_REQUIREMENTS = (ROOT / "requirements.txt").read_text(encoding="utf-8")
TEST_REQUIREMENTS = (ROOT / "test-requirements.txt").read_text(encoding="utf-8")
MAKEFILE = (ROOT / "Makefile").read_text(encoding="utf-8")

RUNTIME_AUDIT = (
    'env -u PYTHONPATH "$$PYTHON" -I -B -m pip_audit -r "$$ROOT/requirements.txt"'
)
TEST_AUDIT = (
    'env -u PYTHONPATH "$$PYTHON" -I -B -m pip_audit -r "$$ROOT/test-requirements.txt"'
)


def validate(runtime_requirements, test_requirements, makefile):
    errors = []
    if runtime_requirements.splitlines().count("tornado==6.5.7") != 1:
        errors.append("runtime requirements must pin Tornado 6.5.7 exactly once")
    if test_requirements.splitlines().count("msgpack==1.2.1") != 1:
        errors.append("test requirements must pin patched msgpack 1.2.1 exactly once")
    if makefile.count(RUNTIME_AUDIT) != 1:
        errors.append("make check must audit runtime requirements exactly once")
    if makefile.count(TEST_AUDIT) != 1:
        errors.append("make check must audit test requirements exactly once")
    return errors


baseline_errors = validate(RUNTIME_REQUIREMENTS, TEST_REQUIREMENTS, MAKEFILE)
if baseline_errors:
    raise AssertionError(f"baseline dependency audit is invalid: {baseline_errors}")

mutations = {
    "vulnerable msgpack": (
        RUNTIME_REQUIREMENTS,
        TEST_REQUIREMENTS.replace("msgpack==1.2.1", "msgpack==1.1.2", 1),
        MAKEFILE,
    ),
    "floating msgpack": (
        RUNTIME_REQUIREMENTS,
        TEST_REQUIREMENTS.replace("msgpack==1.2.1", "msgpack>=1.2.1", 1),
        MAKEFILE,
    ),
    "missing runtime audit": (
        RUNTIME_REQUIREMENTS,
        TEST_REQUIREMENTS,
        MAKEFILE.replace(f"\t{RUNTIME_AUDIT}\n", "", 1),
    ),
    "missing test audit": (
        RUNTIME_REQUIREMENTS,
        TEST_REQUIREMENTS,
        MAKEFILE.replace(f"\t{TEST_AUDIT}\n", "", 1),
    ),
    "duplicated runtime audit": (
        RUNTIME_REQUIREMENTS,
        TEST_REQUIREMENTS,
        MAKEFILE.replace(TEST_AUDIT, RUNTIME_AUDIT, 1),
    ),
}

for description, inputs in mutations.items():
    if not validate(*inputs):
        raise AssertionError(f"{description} mutation was accepted")

print(f"dependency audit contract tests passed ({len(mutations)} mutations rejected).")
