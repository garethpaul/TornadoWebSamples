#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = "def _close_invalid_message(self):"
DISCARD = "self.application.chat_clients.discard(self)"
INVALID_CLOSE = "self.close(code=1003, reason='Invalid chat message')"
HELPER_CALL = "self._close_invalid_message()"
HELPER_DISCARD = HELPER + "\n        " + DISCARD


def contract_errors(source, tests):
    errors = []
    for fragment in (HELPER, DISCARD, INVALID_CLOSE):
        if fragment not in source:
            errors.append(f"source contract is missing: {fragment}")
    if source.count(HELPER_CALL) != 2:
        errors.append("malformed JSON and invalid bodies must share invalid-sender cleanup")
    helper_start = source.find(HELPER)
    helper_end = source.find("\n    def ", helper_start + len(HELPER))
    helper = source[helper_start:helper_end] if helper_start >= 0 else ""
    if DISCARD not in helper or INVALID_CLOSE not in helper:
        errors.append("invalid-message cleanup must discard the sender before closing")
    elif helper.find(DISCARD) > helper.find(INVALID_CLOSE):
        errors.append("invalid-message cleanup must discard before closing")
    for fragment in (
        "test_socket_message_validation_closes_invalid_frames",
        "assert handler.application.chat_clients == {client}",
        'assert closed == [(1003, "Invalid chat message")]',
    ):
        if fragment not in tests:
            errors.append(f"unit coverage is missing: {fragment}")
    return errors


def main():
    source = (ROOT / "socket_chat" / "application.py").read_text(encoding="utf-8")
    tests = (ROOT / "tests" / "test_chat_handlers.py").read_text(encoding="utf-8")
    baseline_errors = contract_errors(source, tests)
    if baseline_errors:
        raise SystemExit("baseline invalid-sender contract failed: " + "; ".join(baseline_errors))

    mutations = {
        "retained invalid sender": (
            HELPER_DISCARD,
            HELPER + "\n        self.application.chat_clients.discard(None)",
        ),
        "close before discard": (
            HELPER_DISCARD + "\n        " + INVALID_CLOSE,
            HELPER + "\n        " + INVALID_CLOSE + "\n        " + DISCARD,
        ),
        "malformed JSON bypass": (HELPER_CALL, INVALID_CLOSE),
    }
    last_call = source.rfind(HELPER_CALL)
    mutations["invalid body bypass"] = (last_call, INVALID_CLOSE)
    for name, mutation in mutations.items():
        if isinstance(mutation[0], int):
            index, replacement = mutation
            if index < 0:
                raise SystemExit(f"mutation setup failed for {name}")
            mutated = source[:index] + replacement + source[index + len(HELPER_CALL):]
        else:
            old, replacement = mutation
            mutated = source.replace(old, replacement, 1)
        if mutated == source:
            raise SystemExit(f"mutation setup failed for {name}")
        if not contract_errors(mutated, tests):
            raise SystemExit(f"invalid-sender contract accepted {name}")

    print(f"WebSocket invalid-sender contract passed ({len(mutations)} mutations rejected)")


if __name__ == "__main__":
    main()
