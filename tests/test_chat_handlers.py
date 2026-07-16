import asyncio
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeferredDelivery:
    def __init__(self, error=None):
        self.callback = None
        self.error = error

    def add_done_callback(self, callback):
        self.callback = callback

    def result(self):
        if self.error is not None:
            raise self.error

    def finish(self):
        assert self.callback is not None
        self.callback(self)


class DeferredClient:
    def __init__(self, error=None):
        self.delivery = DeferredDelivery(error)

    def write_message(self, message):
        return self.delivery


def test_comet_messages_notify_and_clear_callbacks():
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    received = []

    messages.register_callback(received.append)
    messages.add("hello")

    assert received == ["hello"]
    assert messages.callbacks == []


def test_comet_application_bounds_request_bodies():
    comet = load_module("comet_body_limit_app", "comet_chat/application.py")

    assert comet.http_server_options() == {"max_body_size": 4096}
    assert comet.MAX_COMET_REQUEST_BODY_SIZE > comet.MAX_MESSAGE_LENGTH * 4


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


def test_comet_messages_bound_pending_callbacks_and_reuse_removed_slot():
    comet = load_module("comet_capacity_app", "comet_chat/application.py")
    messages = comet.Messages(max_callbacks=2)
    first = lambda message: message
    second = lambda message: message
    rejected = lambda message: message

    assert messages.register_callback(first)
    assert messages.register_callback(second)
    assert not messages.register_callback(rejected)
    assert messages.callbacks == [first, second]

    messages.remove_callback(first)

    assert messages.register_callback(rejected)
    assert messages.callbacks == [second, rejected]


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


def test_comet_handler_times_out_and_cleans_up_long_poll(monkeypatch):
    comet = load_module("comet_app", "comet_chat/application.py")
    messages = comet.Messages()
    statuses = []
    delivered = []

    async def timeout_wait(message_future, timeout):
        assert timeout == comet.COMET_LONG_POLL_TIMEOUT_SECONDS
        message_future.cancel()
        raise asyncio.TimeoutError

    monkeypatch.setattr(comet.asyncio, "wait_for", timeout_wait)
    handler = comet.MessageHandler.__new__(comet.MessageHandler)
    handler.application = type("Application", (), {
        "chat_messages": messages,
    })()
    handler.set_status = statuses.append
    handler.on_message = delivered.append

    asyncio.run(handler.get())

    assert statuses == [204]
    assert delivered == []
    assert messages.callbacks == []
    assert handler._message_callback is None
    assert handler._message_future is None


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


def test_socket_client_admission_bounds_registry_and_reuses_slot():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    application = socket_app.Application(max_chat_clients=1)
    first = object()
    overloaded = object()
    replacement = object()

    assert application.register_chat_client(first)
    assert application.register_chat_client(first)
    assert not application.register_chat_client(overloaded)
    assert application.chat_clients == {first}

    application.chat_clients.discard(first)

    assert application.register_chat_client(replacement)
    assert application.chat_clients == {replacement}


def test_socket_message_rate_limiter_bounds_and_expires_rolling_window():
    socket_app = load_module("socket_rate_limit_app", "socket_chat/application.py")
    now = [10.0]
    limiter = socket_app.MessageRateLimiter(2, 1, clock=lambda: now[0])

    assert limiter.allow()
    assert limiter.allow()
    assert not limiter.allow()

    now[0] = 11.0

    assert limiter.allow()
    assert len(limiter.timestamps) == 1


def test_socket_message_rate_limiters_are_independent_per_connection():
    socket_app = load_module("socket_rate_isolation_app", "socket_chat/application.py")
    first = socket_app.MessageRateLimiter(1, 60, clock=lambda: 10.0)
    second = socket_app.MessageRateLimiter(1, 60, clock=lambda: 10.0)

    assert first.allow()
    assert not first.allow()
    assert second.allow()


def test_socket_message_rate_limit_discards_client_before_close():
    socket_app = load_module("socket_rate_close_app", "socket_chat/application.py")
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler._message_rate_limiter = type(
        "RejectingLimiter", (), {"allow": lambda self: False}
    )()
    handler.application = type("Application", (), {"chat_clients": {handler}})()
    closed = []
    handler.close = lambda code=None, reason=None: closed.append((code, reason))

    handler.on_message("not-json")

    assert handler.application.chat_clients == set()
    assert closed == [(1008, "Message rate limit exceeded")]


def test_socket_unregistered_handler_cannot_broadcast():
    socket_app = load_module(
        "socket_unregistered_sender_app", "socket_chat/application.py"
    )

    class Client:
        def __init__(self):
            self.messages = []

        def write_message(self, message):
            self.messages.append(message)

    client = Client()
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.application = type("Application", (), {"chat_clients": {client}})()

    handler.on_message('{"body": "hello"}')

    assert client.messages == []


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
    handler.write_message = lambda message: None
    handler.application = type("Application", (), {"chat_clients": {handler, client}})()

    handler.on_message('{"body": "hello"}')

    assert client.messages == ["hello"]


def test_socket_message_keeps_client_after_async_delivery_succeeds():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    client = DeferredClient()
    clients = {client}
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.write_message = lambda message: None
    clients.add(handler)
    handler.application = type("Application", (), {"chat_clients": clients})()

    handler.on_message('{"body": "hello"}')
    client.delivery.finish()

    assert client in clients


def test_socket_message_discards_client_after_async_delivery_fails():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    client = DeferredClient(RuntimeError("stream closed"))
    clients = {client}
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.write_message = lambda message: None
    clients.add(handler)
    handler.application = type("Application", (), {"chat_clients": clients})()

    handler.on_message('{"body": "hello"}')

    assert client in clients

    client.delivery.finish()

    assert client not in clients


def test_socket_message_discards_client_after_async_delivery_is_cancelled():
    socket_app = load_module("socket_app", "socket_chat/application.py")
    client = DeferredClient(asyncio.CancelledError())
    clients = {client}
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.write_message = lambda message: None
    clients.add(handler)
    handler.application = type("Application", (), {"chat_clients": clients})()

    handler.on_message('{"body": "hello"}')
    client.delivery.finish()

    assert client not in clients


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
    handler.write_message = lambda message: None
    handler.application = type("Application", (), {
        "chat_clients": OrderedCallbacks([handler, failing_client, client]),
    })()

    handler.on_message('{"body": "hello"}')

    assert client.messages == ["hello"]
    assert failing_client not in handler.application.chat_clients
    assert client in handler.application.chat_clients


def test_socket_message_validation_removes_invalid_senders_before_close():
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
        handler.application = type(
            "Application", (), {"chat_clients": {handler, client}}
        )()

        handler.on_message(frame)

        assert client.messages == []
        assert handler.application.chat_clients == {client}
        assert closed == [(1003, "Invalid chat message")]

        handler.on_message('{"body": "late message"}')

        assert client.messages == []


def test_socket_message_validation_trims_body_before_broadcast():
    socket_app = load_module("socket_app", "socket_chat/application.py")

    class Client:
        def __init__(self):
            self.messages = []

        def write_message(self, message):
            self.messages.append(message)

    client = Client()
    handler = socket_app.MessageHandler.__new__(socket_app.MessageHandler)
    handler.write_message = lambda message: None
    handler.application = type("Application", (), {"chat_clients": {handler, client}})()

    handler.on_message('{"body": "  hello  "}')

    assert client.messages == ["hello"]
