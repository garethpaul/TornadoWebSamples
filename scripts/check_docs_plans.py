#!/usr/bin/env python3
from pathlib import Path
import re
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
ROOT_OVERRIDE_PLAN = DOCS_PLANS / "2026-06-14-make-root-override-protection.md"
MAKE_AUTHORITY_PLAN = DOCS_PLANS / "2026-06-21-make-authority-isolation.md"
COMET_PENDING_POLL_PLAN = DOCS_PLANS / "2026-06-15-comet-pending-poll-cap.md"
SOCKET_CLIENT_CAP_PLAN = DOCS_PLANS / "2026-06-17-websocket-client-cap.md"
SOCKET_MESSAGE_RATE_PLAN = DOCS_PLANS / "2026-06-17-websocket-message-rate-limit.md"
DEPENDENCY_AUDIT_PLAN = DOCS_PLANS / "2026-06-20-development-dependency-audit.md"
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
    if not ROOT_OVERRIDE_PLAN.exists():
        failures.append("docs/plans/2026-06-14-make-root-override-protection.md is missing")
    if not MAKE_AUTHORITY_PLAN.exists():
        failures.append("docs/plans/2026-06-21-make-authority-isolation.md is missing")
    if not COMET_PENDING_POLL_PLAN.exists():
        failures.append("docs/plans/2026-06-15-comet-pending-poll-cap.md is missing")
    if not SOCKET_CLIENT_CAP_PLAN.exists():
        failures.append("docs/plans/2026-06-17-websocket-client-cap.md is missing")
    if not SOCKET_MESSAGE_RATE_PLAN.exists():
        failures.append("docs/plans/2026-06-17-websocket-message-rate-limit.md is missing")
    if not DEPENDENCY_AUDIT_PLAN.exists():
        failures.append("docs/plans/2026-06-20-development-dependency-audit.md is missing")
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
            "Tornado is pinned to 6.5.7",
            "Comet long polls expire after 25 seconds",
            "Comet request bodies are capped at 4096 bytes",
            "Comet accepts at most 100 pending long polls",
            "WebSocket accepts at most 100 connected clients",
            "Development dependencies pin msgpack 1.2.1",
        ),
        "SECURITY.md": (
            "25-second server-side lifetime",
            "Comet request bodies are capped at 4096 bytes",
            "Comet accepts at most 100 pending long polls",
            "WebSocket accepts at most 100 connected clients",
        ),
        "VISION.md": (
            "Keep idle comet long polls bounded",
            "Bound comet request bodies before form parsing",
            "Cap pending comet long polls at 100",
            "Cap connected WebSocket clients at 100",
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
    for contract in (
        "def has_capacity(self):",
        "len(self.callbacks) < self.max_callbacks",
        "if not self.application.chat_messages.has_capacity():",
        "self.set_status(503)",
        "self.set_header('Retry-After', str(COMET_OVERLOAD_RETRY_SECONDS))",
    ):
        if contract not in comet:
            failures.append(f"comet pending-poll capacity contract is missing: {contract}")
    for name, value in (
        ("MAX_PENDING_COMET_POLLS", 100),
        ("COMET_OVERLOAD_RETRY_SECONDS", 1),
    ):
        if not re.search(rf"^{name} = {value}$", comet, re.MULTILINE):
            failures.append(f"comet pending-poll constant is missing: {name} = {value}")
    capacity_check = comet.find("if not self.application.chat_messages.has_capacity():")
    future_allocation = comet.find("asyncio.get_running_loop().create_future()")
    if capacity_check < 0 or future_allocation < 0 or capacity_check > future_allocation:
        failures.append("comet capacity must be checked before long-poll future allocation")
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
    if "if self not in self.application.chat_clients:" not in socket:
        failures.append("socket MessageHandler must ignore messages from unregistered handlers")
    for contract in (
        "MAX_WEBSOCKET_CLIENTS = 100",
        "WEBSOCKET_OVERLOAD_CLOSE_CODE = 1013",
        "WEBSOCKET_OVERLOAD_CLOSE_REASON = 'Chat capacity reached'",
        "max_chat_clients=MAX_WEBSOCKET_CLIENTS,",
        "def register_chat_client(self, client):",
        "if len(self.chat_clients) >= self.max_chat_clients:",
        "if not self.application.register_chat_client(self):",
        "code=WEBSOCKET_OVERLOAD_CLOSE_CODE",
        "reason=WEBSOCKET_OVERLOAD_CLOSE_REASON",
    ):
        if contract not in socket:
            failures.append(f"WebSocket client-cap contract is missing: {contract}")
    for contract in (
        "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10",
        "WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS = 1",
        "WEBSOCKET_RATE_LIMIT_CLOSE_CODE = 1008",
        "WEBSOCKET_RATE_LIMIT_CLOSE_REASON = 'Message rate limit exceeded'",
        "class MessageRateLimiter(object):",
        "while self.timestamps and self.timestamps[0] <= cutoff:",
        "self._message_rate_limiter = MessageRateLimiter(",
        "if not self._message_rate_limiter.allow():",
        "self.application.chat_clients.discard(self)",
        "code=WEBSOCKET_RATE_LIMIT_CLOSE_CODE",
        "reason=WEBSOCKET_RATE_LIMIT_CLOSE_REASON",
    ):
        if contract not in socket:
            failures.append(f"WebSocket message-rate contract is missing: {contract}")
    if socket.count("self._message_rate_limiter = MessageRateLimiter(") != 2:
        failures.append("WebSocket handlers must own limiters in lifecycle and direct-test paths")
    if socket.count("self.application.chat_clients.discard(self)") != 2:
        failures.append("WebSocket close and rate-overload paths must discard the handler")
    rate_check = "if not self._message_rate_limiter.allow():"
    json_decode = "parsed = tornado.escape.json_decode(message)"
    if rate_check in socket and json_decode in socket and (
            socket.index(rate_check) > socket.index(json_decode)):
        failures.append("WebSocket message-rate enforcement must precede JSON parsing")

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
        "test_comet_messages_bound_pending_callbacks_and_reuse_removed_slot",
        "Messages(max_callbacks=2)",
        "assert not messages.register_callback(rejected)",
    ):
        if contract not in handler_tests:
            failures.append(f"comet pending-poll unit contract is missing: {contract}")
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
    for contract in (
        "test_socket_client_admission_bounds_registry_and_reuses_slot",
        "test_socket_unregistered_handler_cannot_broadcast",
        "Application(max_chat_clients=1)",
        "assert not application.register_chat_client(overloaded)",
        "assert application.register_chat_client(replacement)",
        "assert client.messages == []",
    ):
        if contract not in handler_tests:
            failures.append(f"WebSocket client-cap unit contract is missing: {contract}")
    for contract in (
        "test_socket_message_rate_limiter_bounds_and_expires_rolling_window",
        "test_socket_message_rate_limiters_are_independent_per_connection",
        "test_socket_message_rate_limit_discards_client_before_close",
        "now[0] = 11.0",
        "assert second.allow()",
        "assert handler.application.chat_clients == set()",
    ):
        if contract not in handler_tests:
            failures.append(f"WebSocket message-rate unit contract is missing: {contract}")

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    if "tornado==6.5.7" not in requirements:
        failures.append("requirements.txt must pin patched Tornado 6.5.7")
    test_requirements = (ROOT / "test-requirements.txt").read_text(encoding="utf-8")
    for requirement in (
            "msgpack==1.2.1", "pip==26.1.2", "pip-audit==2.10.0",
            "pytest==9.0.3"):
        if requirement not in test_requirements:
            failures.append(f"test-requirements.txt must pin {requirement}")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    root_assignments = re.findall(
        r"^(?:override\s+)?ROOT\s*[:+?]?=", makefile, re.MULTILINE
    )
    if len(root_assignments) != 1:
        failures.append("Makefile must contain exactly one protected repository-root declaration")
    for contract in (
        ".DEFAULT_GOAL := check",
        ".PHONY: __repository-make-authority build check contract-test lint root-test test verify",
        "PUBLIC_TARGETS := build check contract-test lint root-test test verify",
        "override PYTHON := $(value PYTHON)",
        "PYTHON must be a literal executable path, not Make syntax",
        "override SHELL := /bin/sh",
        "MAKEFLAGS must not be overridden for repository verification",
        "non-executing or error-ignoring MAKEFLAGS are not supported",
        "MAKEFILES must be empty",
        "MAKEFILE_LIST must not be overridden",
        "$(PUBLIC_TARGETS): override SHELL := /bin/sh",
        "$(PUBLIC_TARGETS): override .SHELLFLAGS := -c",
        "$(PUBLIC_TARGETS): override ROOT := $(REPOSITORY_ROOT)",
        "$(PUBLIC_TARGETS): override PYTHON := $(value PYTHON)",
        "$(PUBLIC_TARGETS):: __repository-make-authority",
        "build:: lint",
        "root-test::",
        '"$$ROOT/scripts/test-makefile-root.sh"',
        "verify:: root-test lint contract-test test build",
        "check:: verify",
        '"$$ROOT/comet_chat/application.py"',
        '"$$ROOT/socket_chat/application.py"',
        '"$$ROOT/scripts/check_docs_plans.py"',
        '"$$ROOT/scripts/test_dependency_audit_contract.py"',
        '"$$ROOT/scripts/test_workflow_contract.py"',
        'env -u PYTHONPATH "$$PYTHON" -m pip check',
        'pip_audit -r "$$ROOT/requirements.txt"',
        'pip_audit -r "$$ROOT/test-requirements.txt"',
    ):
        if contract not in makefile:
            failures.append(f"Makefile verification contract is missing: {contract}")

    if "docs/plans/2026-06-14-make-root-override-protection.md" not in (
        ROOT / "README.md"
    ).read_text(encoding="utf-8"):
        failures.append("README.md must index Make root override protection evidence")
    if "docs/plans/2026-06-21-make-authority-isolation.md" not in (
        ROOT / "README.md"
    ).read_text(encoding="utf-8"):
        failures.append("README.md must index Make authority isolation evidence")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    make_authority_plan = MAKE_AUTHORITY_PLAN.read_text(encoding="utf-8")
    for path, document in (("README.md", readme), (str(MAKE_AUTHORITY_PLAN.relative_to(ROOT)), make_authority_plan)):
        normalized_document = " ".join(document.split())
        for boundary in (
            "GNU Make `override` directives",
            "startup files",
            "caller-added double-colon recipes",
            "PATH resolution of the default `python3`",
        ):
            if boundary not in normalized_document:
                failures.append(f"{path} must document the caller Make boundary: {boundary}")

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
        "test_long_poll_capacity_rejects_overload_and_reuses_slot",
        'assert overloaded.code == 503',
        'assert overloaded.headers["Retry-After"] == "1"',
        "test_websocket_capacity_closes_overload_and_reuses_slot",
        "assert overloaded.close_code == 1013",
        'assert overloaded.close_reason == "Chat capacity reached"',
        "test_websocket_rejects_oversized_frame_before_broadcast",
        "assert client.close_code == 1009",
        "test_websocket_message_rate_limit_closes_offending_client",
        "assert client.close_code == 1008",
        'assert client.close_reason == "Message rate limit exceeded"',
        "assert len(self._app.chat_clients) == 1",
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

    if COMET_PENDING_POLL_PLAN.exists():
        pending_poll_plan = COMET_PENDING_POLL_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory pinned `make check` passed",
            "hostile pending-poll mutations were rejected",
        ):
            if evidence not in pending_poll_plan:
                failures.append(
                    f"{COMET_PENDING_POLL_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )

    if SOCKET_CLIENT_CAP_PLAN.exists():
        socket_client_cap_plan = SOCKET_CLIENT_CAP_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory pinned `make check` passed",
            "hostile WebSocket client-cap mutations were rejected",
        ):
            if evidence not in socket_client_cap_plan:
                failures.append(
                    f"{SOCKET_CLIENT_CAP_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )
    if SOCKET_MESSAGE_RATE_PLAN.exists():
        socket_message_rate_plan = SOCKET_MESSAGE_RATE_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory pinned `make check` passed",
            "hostile WebSocket message-rate mutations were rejected",
        ):
            if evidence not in socket_message_rate_plan:
                failures.append(
                    f"{SOCKET_MESSAGE_RATE_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )
    if DEPENDENCY_AUDIT_PLAN.exists():
        dependency_audit_plan = DEPENDENCY_AUDIT_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory `make check` passed",
            "five hostile dependency-audit mutations were rejected",
        ):
            if evidence not in dependency_audit_plan:
                failures.append(
                    f"{DEPENDENCY_AUDIT_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )

    for relative_path in ("AGENTS.md", "CHANGES.md"):
        if "Comet accepts at most 100 pending long polls" not in (
            ROOT / relative_path
        ).read_text(encoding="utf-8"):
            failures.append(f"{relative_path} must document the pending comet poll cap")
        if "WebSocket accepts at most 100 connected clients" not in (
            ROOT / relative_path
        ).read_text(encoding="utf-8"):
            failures.append(f"{relative_path} must document the WebSocket client cap")
        if "WebSocket accepts at most 10 messages per second per connection" not in (
            ROOT / relative_path
        ).read_text(encoding="utf-8"):
            failures.append(f"{relative_path} must document the WebSocket message-rate limit")

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
