#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-tornado-web-samples-baseline.md"
COMET_DISPATCH_PLAN = DOCS_PLANS / "2026-06-09-comet-callback-dispatch-snapshot.md"
COMET_EXCEPTION_PLAN = DOCS_PLANS / "2026-06-09-comet-callback-exception-isolation.md"
SOCKET_EXCEPTION_PLAN = DOCS_PLANS / "2026-06-09-websocket-callback-exception-isolation.md"
CI_PLAN = DOCS_PLANS / "2026-06-10-ci-baseline.md"
OFFLINE_CLIENT_PLAN = DOCS_PLANS / "2026-06-10-offline-browser-clients.md"
SOCKET_REGISTRY_PLAN = DOCS_PLANS / "2026-06-10-websocket-client-registry.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "check.yml"


def main():
    failures = []

    if not CANONICAL_PLAN.exists():
        failures.append("docs/plans/2026-06-08-tornado-web-samples-baseline.md is missing")
    if not COMET_DISPATCH_PLAN.exists():
        failures.append("docs/plans/2026-06-09-comet-callback-dispatch-snapshot.md is missing")
    if not COMET_EXCEPTION_PLAN.exists():
        failures.append("docs/plans/2026-06-09-comet-callback-exception-isolation.md is missing")
    if not SOCKET_EXCEPTION_PLAN.exists():
        failures.append("docs/plans/2026-06-09-websocket-callback-exception-isolation.md is missing")
    if not CI_PLAN.exists():
        failures.append("docs/plans/2026-06-10-ci-baseline.md is missing")
    if not OFFLINE_CLIENT_PLAN.exists():
        failures.append("docs/plans/2026-06-10-offline-browser-clients.md is missing")
    if not SOCKET_REGISTRY_PLAN.exists():
        failures.append("docs/plans/2026-06-10-websocket-client-registry.md is missing")
    if not CI_WORKFLOW.exists():
        failures.append(".github/workflows/check.yml is missing")

    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.exists() else []
    if not plans:
        failures.append("docs/plans must contain at least one completed plan")

    for plan_path in plans:
        plan = plan_path.read_text(encoding="utf-8")
        if "Status: Completed" not in plan or "make check" not in plan:
            failures.append(f"{plan_path.relative_to(ROOT)} must record completed status and make check verification")

    if CI_WORKFLOW.exists():
        workflow = CI_WORKFLOW.read_text(encoding="utf-8")
        for phrase in [
            "permissions:\n  contents: read",
            "workflow_dispatch:",
            "concurrency:",
            "cancel-in-progress: true",
            "runs-on: ubuntu-24.04",
            "timeout-minutes: 10",
            "python-version: ['3.10', '3.12', '3.14']",
            "fail-fast: false",
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3",
            "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0",
            "requirements.txt",
            "test-requirements.txt",
            "run: make check",
        ]:
            if phrase not in workflow:
                failures.append(f".github/workflows/check.yml must include {phrase}")

    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "VISION.md", "SECURITY.md"]
    )
    if "GitHub Actions" not in docs:
        failures.append("project docs must mention the GitHub Actions baseline")

    comet = (ROOT / "comet_chat" / "application.py").read_text(encoding="utf-8")
    if "@tornado.web.asynchronous" in comet or "self.async_callback" in comet:
        failures.append("comet MessageHandler must not use removed Tornado 4 async APIs")
    if "async def get(self, *args, **kwargs):" not in comet:
        failures.append("comet MessageHandler.get must use the Tornado 6 awaitable handler API")
    if "asyncio.get_running_loop().create_future()" not in comet:
        failures.append("comet MessageHandler.get must wait on an asyncio future")
    if "message_future.cancel()" not in comet:
        failures.append("comet MessageHandler must cancel its pending future on disconnect")
    if "str(BASE_DIR / 'templates')" not in comet or "str(BASE_DIR / 'static')" not in comet:
        failures.append("comet Application paths must be anchored to the source directory")
    if "http_server.listen(8000, address='127.0.0.1')" not in comet:
        failures.append("comet sample must bind to loopback by default")
    if "def remove_callback(self, callback):" not in comet:
        failures.append("comet Messages must support removing abandoned callbacks")
    if "def on_connection_close(self):" not in comet:
        failures.append("comet MessageHandler must clean up callbacks on connection close")
    if "callbacks = self.callbacks" not in comet or "self.callbacks = [] # reset before callbacks fire" not in comet:
        failures.append("comet Messages.add must snapshot and clear callbacks before dispatch")
    if "logger.exception(\"Could not deliver comet chat message\")" not in comet:
        failures.append("comet Messages.add must log callback delivery failures")
    if "except Exception:" not in comet:
        failures.append("comet Messages.add must isolate callback delivery exceptions")
    if "'xsrf_cookies' : True" not in comet:
        failures.append("comet Application must enable Tornado XSRF cookies")

    socket = (ROOT / "socket_chat" / "application.py").read_text(encoding="utf-8")
    if "str(BASE_DIR / 'templates')" not in socket or "str(BASE_DIR / 'static')" not in socket:
        failures.append("socket Application paths must be anchored to the source directory")
    if "http_server.listen(8000, address='127.0.0.1')" not in socket:
        failures.append("socket sample must bind to loopback by default")
    if "logger.exception(\"Could not deliver websocket chat message\")" not in socket:
        failures.append("socket MessageHandler.on_message must log callback delivery failures")
    if "except Exception:" not in socket:
        failures.append("socket MessageHandler.on_message must isolate callback delivery exceptions")
    if "self.application.chat_clients.discard(cb)" not in socket:
        failures.append("socket MessageHandler.on_message must discard callbacks that fail delivery")
    if "self.chat_clients = set()" not in socket:
        failures.append("socket Application must own its connected client registry")
    if "callbacks = set()" in socket:
        failures.append("socket clients must not be stored on the handler class")

    handler_tests = (ROOT / "tests" / "test_chat_handlers.py").read_text(encoding="utf-8")
    if "test_socket_clients_are_isolated_per_application" not in handler_tests:
        failures.append("socket application client-registry isolation coverage is missing")

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    if "tornado==6.5.6" not in requirements:
        failures.append("requirements.txt must pin Tornado 6.5.6")
    test_requirements = (ROOT / "test-requirements.txt").read_text(encoding="utf-8")
    for requirement in ("pip==26.1.2", "pip-audit==2.10.0", "pytest==9.0.3"):
        if requirement not in test_requirements:
            failures.append(f"test-requirements.txt must pin {requirement}")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for contract in (
        "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))",
        "env -u PYTHONPATH $(PYTHON) -m pip check",
        'pip_audit -r "$(ROOT)/requirements.txt"',
    ):
        if contract not in makefile:
            failures.append(f"Makefile verification contract is missing: {contract}")

    templates = [
        (ROOT / "comet_chat" / "templates" / "index.html").read_text(encoding="utf-8"),
        (ROOT / "socket_chat" / "templates" / "index.html").read_text(encoding="utf-8"),
    ]
    for template in templates:
        if "http://" in template or "https://" in template:
            failures.append("chat templates must not load third-party network assets")
        if 'action="/message"' not in template or 'name="message"' not in template:
            failures.append("chat forms must submit message fields to the same-origin endpoint")
    if "{% module xsrf_form_html() %}" not in templates[0]:
        failures.append("comet template must render Tornado's XSRF form token")

    for client_path in (
        ROOT / "comet_chat" / "static" / "cometchat.coffee",
        ROOT / "comet_chat" / "static" / "cometchat.js",
        ROOT / "socket_chat" / "static" / "socketchat.coffee",
        ROOT / "socket_chat" / "static" / "socketchat.js",
    ):
        client = client_path.read_text(encoding="utf-8")
        if "jQuery" in client or "$.ajax" in client:
            failures.append(f"{client_path.relative_to(ROOT)} must use native browser APIs")
        if "document.createElement" not in client or ".textContent" not in client:
            failures.append(f"{client_path.relative_to(ROOT)} must render messages as text nodes")

    runtime_tests = (ROOT / "tests" / "test_tornado6_runtime.py").read_text(encoding="utf-8")
    for test_name in (
        "test_comet_post_rejects_missing_xsrf_token",
        "test_comet_post_accepts_rendered_xsrf_token",
    ):
        if test_name not in runtime_tests:
            failures.append(f"runtime XSRF coverage is missing: {test_name}")

    if failures:
        print("Documentation plan checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Documentation plan checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
