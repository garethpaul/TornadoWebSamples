#!/usr/bin/env python3
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
# Whole-line pins: a bare substring accepts any widening that extends the
# reviewed literal, so "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10" would match a
# shipped value of 10000.
RATE_CONSTANTS = (
    ("MAX_WEBSOCKET_MESSAGES_PER_WINDOW", 10),
    ("WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS", 1),
    ("WEBSOCKET_RATE_LIMIT_CLOSE_CODE", 1008),
)
RATE_CHECK = "if not self._message_rate_limiter.allow():"
RATE_DISCARD = RATE_CHECK + "\n            self.application.chat_clients.discard(self)"
JSON_DECODE = "parsed = tornado.escape.json_decode(message)"
EXPIRY = "while self.timestamps and self.timestamps[0] <= cutoff:"


def contract_errors(source, unit_tests, runtime_tests):
    errors = []
    for name, value in RATE_CONSTANTS:
        if not re.search(
            rf"^{re.escape(name)} = {re.escape(str(value))}$", source, re.MULTILINE
        ):
            errors.append(f"source bound must be declared exactly as: {name} = {value}")
    for fragment in (
        "WEBSOCKET_RATE_LIMIT_CLOSE_REASON = 'Message rate limit exceeded'",
        "class MessageRateLimiter(object):",
        EXPIRY,
        "self.timestamps.popleft()",
        "if len(self.timestamps) >= self.max_messages:",
        "self._message_rate_limiter = MessageRateLimiter(",
        RATE_CHECK,
        "self.application.chat_clients.discard(self)",
        "code=WEBSOCKET_RATE_LIMIT_CLOSE_CODE",
        "reason=WEBSOCKET_RATE_LIMIT_CLOSE_REASON",
    ):
        if fragment not in source:
            errors.append(f"source contract is missing: {fragment}")
    if source.count("self._message_rate_limiter = MessageRateLimiter(") != 2:
        errors.append("open and direct-handler paths must each create an owned limiter")
    if "self.application._message_rate_limiter" in source:
        errors.append("message-rate limiters must not be shared by the application")
    if source.count("self.application.chat_clients.discard(self)") != 3:
        errors.append("close, invalid-message, and rate-overload paths must discard the handler")
    if RATE_DISCARD not in source:
        errors.append("rate-overload rejection must discard the handler before close")
    if RATE_CHECK in source and JSON_DECODE in source:
        if source.index(RATE_CHECK) > source.index(JSON_DECODE):
            errors.append("message-rate enforcement must run before JSON decoding")
    for fragment in (
        "test_socket_message_rate_limiter_bounds_and_expires_rolling_window",
        "assert not limiter.allow()",
        "now[0] = 11.0",
        "test_socket_message_rate_limiters_are_independent_per_connection",
        "test_socket_message_rate_limit_discards_client_before_close",
        "assert second.allow()",
        "assert handler.application.chat_clients == set()",
        # Every other rate test injects an explicit limit, so only this fixture
        # can observe the shipped default moving.
        "test_socket_default_message_rate_is_ten_per_second",
        "assert socket_app.MAX_WEBSOCKET_MESSAGES_PER_WINDOW == 10",
        "assert application.max_messages_per_window == 10",
        "assert [limiter.allow() for _ in range(10)] == [True] * 10",
    ):
        if fragment not in unit_tests:
            errors.append(f"unit coverage is missing: {fragment}")
    for fragment in (
        "test_websocket_message_rate_limit_closes_offending_client",
        "max_messages_per_window=1",
        "message_rate_window_seconds=60",
        "assert client.close_code == 1008",
        'assert client.close_reason == "Message rate limit exceeded"',
    ):
        if fragment not in runtime_tests:
            errors.append(f"runtime coverage is missing: {fragment}")
    return errors


def main():
    source = (ROOT / "socket_chat" / "application.py").read_text(encoding="utf-8")
    unit_tests = (ROOT / "tests" / "test_chat_handlers.py").read_text(encoding="utf-8")
    runtime_tests = (ROOT / "tests" / "test_tornado6_runtime.py").read_text(
        encoding="utf-8"
    )
    baseline_errors = contract_errors(source, unit_tests, runtime_tests)
    if baseline_errors:
        raise SystemExit("baseline rate contract failed: " + "; ".join(baseline_errors))

    mutations = {
        "removed enforcement": (RATE_CHECK, "if False:"),
        "unconditional rejection": (RATE_CHECK, "if True:"),
        "post-parse enforcement": (
            RATE_CHECK,
            JSON_DECODE + "\n        " + RATE_CHECK,
        ),
        "removed expiry": (EXPIRY, "while False:"),
        "non-expiring comparison": ("self.timestamps[0] <= cutoff", "False"),
        "disabled count bound": (
            "if len(self.timestamps) >= self.max_messages:",
            "if False:",
        ),
        "shared limiter": (
            "self._message_rate_limiter = MessageRateLimiter(",
            "self.application._message_rate_limiter = MessageRateLimiter(",
        ),
        "wrong close code": (
            "WEBSOCKET_RATE_LIMIT_CLOSE_CODE = 1008",
            "WEBSOCKET_RATE_LIMIT_CLOSE_CODE = 1013",
        ),
        "retained overloaded client": (
            RATE_DISCARD,
            RATE_CHECK + "\n            self.application.chat_clients.discard(None)",
        ),
        "widened rate limit": (
            "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10",
            "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10000",
        ),
        "appended rate multiplier": (
            "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10",
            "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10 * 10**6",
        ),
        "shortened rate window": (
            "WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS = 1",
            "WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS = 1e-9",
        ),
    }
    for name, (old, new) in mutations.items():
        mutated = source.replace(old, new, 1)
        if mutated == source:
            raise SystemExit(f"mutation setup failed for {name}")
        if not contract_errors(mutated, unit_tests, runtime_tests):
            raise SystemExit(f"rate contract accepted {name}")

    # The default-rate fixture is the only observer of the shipped default, so
    # prove the contract notices its removal.
    unit_mutations = {
        "deleted default-rate fixture": (
            "def test_socket_default_message_rate_is_ten_per_second():",
            "def _disabled_default_message_rate():",
        ),
        "injected default-rate fixture": (
            "assert application.max_messages_per_window == 10",
            "assert application.max_messages_per_window == limit",
        ),
    }
    for name, (old, new) in unit_mutations.items():
        mutated_tests = unit_tests.replace(old, new, 1)
        if mutated_tests == unit_tests:
            raise SystemExit(f"unit mutation setup failed for {name}")
        if not contract_errors(source, mutated_tests, runtime_tests):
            raise SystemExit(f"rate contract accepted {name}")

    print(
        "WebSocket message-rate contract passed "
        f"({len(mutations)} source and {len(unit_mutations)} coverage mutations rejected)"
    )


if __name__ == "__main__":
    main()
