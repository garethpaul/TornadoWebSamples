import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_comet_messages_notify_and_clear_callbacks():
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    received = []

    messages.register_callback(received.append)
    messages.add("hello")

    assert received == ["hello"]
    assert messages.callbacks == []


def test_comet_message_normalization_trims_and_bounds_input():
    comet = load_module("comet_app", "comet_chat/application.py")

    assert comet.normalize_message("  hello  ") == "hello"
    assert comet.normalize_message("") is None
    assert comet.normalize_message("   ") is None
    assert comet.normalize_message(None) is None
    assert comet.normalize_message("x" * (comet.MAX_MESSAGE_LENGTH + 1)) is None


def test_socket_close_is_idempotent():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    socket_app.MessageHandler.callbacks = set()

    handler.on_close()
    handler.on_close()

    assert handler not in socket_app.MessageHandler.callbacks


def test_socket_check_origin_allows_same_host_only():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.request = type("Request", (), {
        "headers": {"Host": "chat.example.test:8000"},
    })()

    assert handler.check_origin("http://chat.example.test:8000")
    assert handler.check_origin("https://chat.example.test:8000")
    assert handler.check_origin("https://CHAT.EXAMPLE.TEST:8000/")
    assert not handler.check_origin("https://other.example.test:8000")
    assert not handler.check_origin("")


def test_socket_message_broadcasts_body_only():
    socket_app = load_module("socket_app", "socket_chat/application.py")

    class Client:
        def __init__(self):
            self.messages = []

        def write_message(self, message):
            self.messages.append(message)

    client = Client()
    socket_app.MessageHandler.callbacks = {client}
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)

    handler.on_message('{"body": "hello"}')

    assert client.messages == ["hello"]


def test_socket_message_validation_closes_invalid_frames():
    socket_app = load_module("socket_app", "socket_chat/application.py")

    class Client:
        def __init__(self):
            self.messages = []

        def write_message(self, message):
            self.messages.append(message)

    for frame in (
        "not-json",
        "[]",
        "{}",
        '{"body": 123}',
        '{"body": ""}',
        '{"body": "   "}',
        '{"body": "%s"}' % ("x" * (socket_app.MAX_MESSAGE_LENGTH + 1)),
    ):
        client = Client()
        handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
        closed = []
        handler.close = lambda code=None, reason=None: closed.append((code, reason))
        socket_app.MessageHandler.callbacks = {client}

        handler.on_message(frame)

        assert client.messages == []
        assert closed == [(1003, "Invalid chat message")]


def test_socket_message_validation_trims_body_before_broadcast():
    socket_app = load_module("socket_app", "socket_chat/application.py")

    class Client:
        def __init__(self):
            self.messages = []

        def write_message(self, message):
            self.messages.append(message)

    client = Client()
    socket_app.MessageHandler.callbacks = {client}
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)

    handler.on_message('{"body": "  hello  "}')

    assert client.messages == ["hello"]
