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


def test_comet_messages_keep_new_callbacks_for_next_dispatch():
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    received = []

    def second_callback(message):
        received.append(("second", message))

    def first_callback(message):
        received.append(("first", message))
        messages.register_callback(second_callback)

    messages.register_callback(first_callback)

    messages.add("hello")

    assert received == [("first", "hello")]
    assert messages.callbacks == [second_callback]

    messages.add("again")

    assert received == [("first", "hello"), ("second", "again")]
    assert messages.callbacks == []


def test_comet_messages_continue_dispatch_after_callback_error():
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    received = []

    def failing_callback(message):
        raise RuntimeError("closed connection")

    messages.register_callback(failing_callback)
    messages.register_callback(received.append)

    messages.add("hello")

    assert received == ["hello"]
    assert messages.callbacks == []


def test_comet_messages_keep_callbacks_per_instance():
    comet = load_module("comet_app", "comet_chat/application.py")
    first = comet.Messages()
    second = comet.Messages()

    first.register_callback(lambda message: message)

    assert len(first.callbacks) == 1
    assert second.callbacks == []


def test_comet_messages_remove_abandoned_callback():
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    callback = lambda message: message

    messages.register_callback(callback)
    messages.remove_callback(callback)
    messages.remove_callback(callback)

    assert messages.callbacks == []


def test_comet_handler_removes_waiting_callback_on_connection_close():
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    callback = lambda message: message

    class PendingFuture:
        def __init__(self):
            self.cancel_count = 0

        def done(self):
            return self.cancel_count > 0

        def cancel(self):
            self.cancel_count += 1

    message_future = PendingFuture()
    handler = comet.MessageHandler.__new__(comet.MessageHandler)
    handler.application = type("Application", (), {
        "chat_messages": messages,
    })()
    handler._message_callback = callback
    handler._message_future = message_future
    messages.register_callback(callback)

    handler.on_connection_close()
    handler.on_connection_close()

    assert messages.callbacks == []
    assert handler._message_callback is None
    assert message_future.cancel_count == 1


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
    handler.application = type("Application", (), {"chat_clients": set()})()

    handler.on_close()
    handler.on_close()

    assert handler not in handler.application.chat_clients


def test_socket_clients_are_isolated_per_application():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    first = socket_app.Application()
    second = socket_app.Application()
    client = object()

    first.chat_clients.add(client)

    assert first.chat_clients == {client}
    assert second.chat_clients == set()


def test_socket_application_bounds_websocket_frames():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    application = socket_app.Application()

    assert socket_app.MAX_WEBSOCKET_FRAME_SIZE == 4096
    assert application.settings["websocket_max_message_size"] == 4096
    assert socket_app.MAX_WEBSOCKET_FRAME_SIZE > socket_app.MAX_MESSAGE_LENGTH * 4


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
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.application = type("Application", (), {"chat_clients": {client}})()

    handler.on_message('{"body": "hello"}')

    assert client.messages == ["hello"]


def test_socket_message_continues_after_client_write_error():
    socket_app = load_module("socket_app", "socket_chat/application.py")

    class OrderedCallbacks:
        def __init__(self, callbacks):
            self.callbacks = callbacks

        def __iter__(self):
            return iter(self.callbacks)

        def __contains__(self, callback):
            return callback in self.callbacks

        def discard(self, callback):
            if callback in self.callbacks:
                self.callbacks.remove(callback)

    class FailingClient:
        def write_message(self, message):
            raise RuntimeError("closed websocket")

    class Client:
        def __init__(self):
            self.messages = []

        def write_message(self, message):
            self.messages.append(message)

    failing_client = FailingClient()
    client = Client()
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.application = type("Application", (), {
        "chat_clients": OrderedCallbacks([failing_client, client]),
    })()

    handler.on_message('{"body": "hello"}')

    assert client.messages == ["hello"]
    assert failing_client not in handler.application.chat_clients
    assert client in handler.application.chat_clients


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
        handler.application = type("Application", (), {"chat_clients": {client}})()

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
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.application = type("Application", (), {"chat_clients": {client}})()

    handler.on_message('{"body": "  hello  "}')

    assert client.messages == ["hello"]
