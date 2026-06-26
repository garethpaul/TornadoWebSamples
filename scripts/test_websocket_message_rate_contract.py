#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RATE_CHECK = "if not self._message_rate_limiter.allow():"
JSON_DECODE = "parsed = tornado.escape.json_decode(message)"
EXPIRY = "while self.timestamps and self.timestamps[0] <= cutoff:"


def contract_errors(source, unit_tests, runtime_tests):
    errors = []
    for fragment in (
        "MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10",
        "WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS = 1",
        "WEBSOCKET_RATE_LIMIT_CLOSE_CODE = 1008",
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
        errors.append("close, rate-overload, and invalid-message paths must discard the handler")
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
            "self.application.chat_clients.discard(self)",
            "self.application.chat_clients.discard(None)",
        ),
    }
    for name, (old, new) in mutations.items():
        mutated = source.replace(old, new, 1)
        if mutated == source:
            raise SystemExit(f"mutation setup failed for {name}")
        if not contract_errors(mutated, unit_tests, runtime_tests):
            raise SystemExit(f"rate contract accepted {name}")

    print(f"WebSocket message-rate contract passed ({len(mutations)} mutations rejected)")


if __name__ == "__main__":
    main()
