#!/usr/bin/env python3
from pathlib import Path
import sys

from workflow_contract import validate as validate_workflow


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-tornado-web-samples-baseline.md"
COMET_DISPATCH_PLAN = DOCS_PLANS / "2026-06-09-comet-callback-dispatch-snapshot.md"
COMET_EXCEPTION_PLAN = DOCS_PLANS / "2026-06-09-comet-callback-exception-isolation.md"
SOCKET_EXCEPTION_PLAN = DOCS_PLANS / "2026-06-09-websocket-callback-exception-isolation.md"
CI_PLAN = DOCS_PLANS / "2026-06-10-ci-baseline.md"
OFFLINE_CLIENT_PLAN = DOCS_PLANS / "2026-06-10-offline-browser-clients.md"
SOCKET_REGISTRY_PLAN = DOCS_PLANS / "2026-06-10-websocket-client-registry.md"
SOCKET_FRAME_LIMIT_PLAN = DOCS_PLANS / "2026-06-12-websocket-frame-limit.md"
SOCKET_ASYNC_DELIVERY_PLAN = DOCS_PLANS / "2026-06-12-websocket-async-delivery-failures.md"
COMET_TIMEOUT_PLAN = DOCS_PLANS / "2026-06-13-comet-long-poll-timeout.md"
COMET_BODY_LIMIT_PLAN = DOCS_PLANS / "2026-06-13-comet-request-body-limit.md"
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
    if not SOCKET_FRAME_LIMIT_PLAN.exists():
        failures.append("docs/plans/2026-06-12-websocket-frame-limit.md is missing")
    if not SOCKET_ASYNC_DELIVERY_PLAN.exists():
        failures.append("docs/plans/2026-06-12-websocket-async-delivery-failures.md is missing")
    if not COMET_TIMEOUT_PLAN.exists():
        failures.append("docs/plans/2026-06-13-comet-long-poll-timeout.md is missing")
    if not COMET_BODY_LIMIT_PLAN.exists():
        failures.append("docs/plans/2026-06-13-comet-request-body-limit.md is missing")
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
        failures.extend(
            f".github/workflows/check.yml must {requirement}"
            for requirement in validate_workflow(workflow)
        )

    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ["README.md", "VISION.md", "SECURITY.md"]
    )
    if "GitHub Actions" not in docs:
        failures.append("project docs must mention the GitHub Actions baseline")
    documentation_contracts = {
        "README.md": (
            "Comet long polls expire after 25 seconds",
            "Comet request bodies are capped at 4096 bytes",
        ),
        "SECURITY.md": (
            "25-second server-side lifetime",
            "Comet request bodies are capped at 4096 bytes",
        ),
        "VISION.md": (
            "Keep idle comet long polls bounded",
            "Bound comet request bodies before form parsing",
        ),
    }
    for relative_path, contracts in documentation_contracts.items():
        document = (ROOT / relative_path).read_text(encoding="utf-8")
        for contract in contracts:
            if contract not in document:
                failures.append(f"{relative_path} must document: {contract}")

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
    for contract in (
        "MAX_COMET_REQUEST_BODY_SIZE = 4096",
        "def http_server_options():",
        "return {'max_body_size': MAX_COMET_REQUEST_BODY_SIZE}",
        "HTTPServer(app, **http_server_options())",
    ):
        if contract not in comet:
            failures.append(f"comet request-body limit contract is missing: {contract}")
    for contract in (
        "COMET_LONG_POLL_TIMEOUT_SECONDS = 25",
        "await asyncio.wait_for(",
        "timeout=COMET_LONG_POLL_TIMEOUT_SECONDS",
        "except asyncio.TimeoutError:",
        "self.set_status(204)",
    ):
        if contract not in comet:
            failures.append(f"comet long-poll timeout contract is missing: {contract}")
    if comet.count("self.application.chat_messages.remove_callback(") < 2:
        failures.append("comet long polls must remove callbacks on completion and disconnect")
    if "self._message_future = None" not in comet:
        failures.append("comet long polls must clear handler-owned future state")

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
    if "MAX_WEBSOCKET_FRAME_SIZE = 4096" not in socket:
        failures.append("socket Application must define the reviewed WebSocket frame limit")
    if "'websocket_max_message_size' : MAX_WEBSOCKET_FRAME_SIZE" not in socket:
        failures.append("socket Application must enforce the WebSocket frame limit before parsing")
    if "delivery.add_done_callback(" not in socket:
        failures.append("socket MessageHandler must observe asynchronous delivery completion")
    if "delivery.result()" not in socket:
        failures.append("socket MessageHandler must consume asynchronous delivery failures")
    if "asyncio.CancelledError" not in socket:
        failures.append("socket MessageHandler must consume cancelled delivery futures")
    if "lambda future, client=cb:" not in socket:
        failures.append("socket MessageHandler must bind each async delivery to its client")
    if "self.application.chat_clients.discard(client)" not in socket:
        failures.append("socket MessageHandler must discard clients after async delivery failures")

    handler_tests = (ROOT / "tests" / "test_chat_handlers.py").read_text(encoding="utf-8")
    if "test_socket_clients_are_isolated_per_application" not in handler_tests:
        failures.append("socket application client-registry isolation coverage is missing")
    for contract in (
        "test_comet_application_bounds_request_bodies",
        'comet.http_server_options() == {"max_body_size": 4096}',
        "MAX_COMET_REQUEST_BODY_SIZE > comet.MAX_MESSAGE_LENGTH * 4",
    ):
        if contract not in handler_tests:
            failures.append(f"comet request-body regression contract is missing: {contract}")
    for contract in (
        "test_comet_handler_times_out_and_cleans_up_long_poll",
        "assert statuses == [204]",
        "assert messages.callbacks == []",
        "assert handler._message_future is None",
    ):
        if contract not in handler_tests:
            failures.append(f"comet timeout regression contract is missing: {contract}")
    for contract in (
        "test_socket_application_bounds_websocket_frames",
        'application.settings["websocket_max_message_size"] == 4096',
        "MAX_WEBSOCKET_FRAME_SIZE > socket_app.MAX_MESSAGE_LENGTH * 4",
    ):
        if contract not in handler_tests:
            failures.append(f"WebSocket frame-limit regression contract is missing: {contract}")
    for contract in (
        "test_socket_message_keeps_client_after_async_delivery_succeeds",
        "test_socket_message_discards_client_after_async_delivery_fails",
        "test_socket_message_discards_client_after_async_delivery_is_cancelled",
        "client.delivery.finish()",
    ):
        if contract not in handler_tests:
            failures.append(f"WebSocket async-delivery regression contract is missing: {contract}")

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
        '"$(ROOT)/scripts/test_workflow_contract.py"',
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
        "test_long_poll_timeout_returns_no_content_and_cleans_up",
        "test_comet_post_rejects_missing_xsrf_token",
        "test_comet_post_accepts_rendered_xsrf_token",
        "test_comet_post_accepts_maximum_browser_form_body",
        "assert len(body) < self.comet.MAX_COMET_REQUEST_BODY_SIZE",
        "test_comet_post_rejects_oversized_request_body",
        "return self.comet.http_server_options()",
        "assert response.code == 400",
        "assert received == []",
    ):
        if test_name not in runtime_tests:
            failures.append(f"runtime coverage is missing: {test_name}")

    static_tests = (ROOT / "tests" / "test_static_assets.py").read_text(encoding="utf-8")
    for contract in (
        "test_comet_client_treats_no_content_as_normal_repoll",
        "response.status is 204",
        "response.status === 204",
        "if (data !== null)",
    ):
        if contract not in static_tests:
            failures.append(f"comet timeout browser coverage is missing: {contract}")

    if failures:
        print("Documentation plan checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Documentation plan checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
