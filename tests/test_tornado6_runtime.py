import asyncio
import importlib.util
import json
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlencode

from tornado.httpclient import HTTPRequest
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.websocket import websocket_connect


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCometApplication(AsyncHTTPTestCase):
    def get_app(self):
        self.comet = load_module("comet_runtime_app", "comet_chat/application.py")
        return self.comet.Application()

    def get_httpserver_options(self):
        return self.comet.http_server_options()

    def _fetch_xsrf_token(self):
        page = self.fetch("/")
        cookies = SimpleCookie()
        for header in page.headers.get_list("Set-Cookie"):
            cookies.load(header)
        return cookies["_xsrf"].value

    @gen_test
    async def test_long_poll_delivers_message_on_tornado_6(self):
        response_future = self.http_client.fetch(self.get_url("/message"))

        for _ in range(100):
            if self._app.chat_messages.callbacks:
                break
            await asyncio.sleep(0.01)

        assert self._app.chat_messages.callbacks

        self._app.chat_messages.add("hello")
        response = await response_future

        assert response.code == 200
        assert json.loads(response.body) == {"message": "hello"}
        assert self._app.chat_messages.callbacks == []

    @gen_test
    async def test_long_poll_timeout_returns_no_content_and_cleans_up(self):
        self.comet.COMET_LONG_POLL_TIMEOUT_SECONDS = 0.01

        response = await self.http_client.fetch(
            self.get_url("/message"),
            raise_error=False,
        )

        assert response.code == 204
        assert response.body == b""
        assert self._app.chat_messages.callbacks == []

    @gen_test
    async def test_long_poll_capacity_rejects_overload_and_reuses_slot(self):
        self._app.chat_messages.max_callbacks = 1
        first_response = self.http_client.fetch(self.get_url("/message"))

        for _ in range(100):
            if len(self._app.chat_messages.callbacks) == 1:
                break
            await asyncio.sleep(0.01)
        assert len(self._app.chat_messages.callbacks) == 1

        overloaded = await self.http_client.fetch(
            self.get_url("/message"),
            raise_error=False,
        )

        assert overloaded.code == 503
        assert overloaded.headers["Retry-After"] == "1"
        assert len(self._app.chat_messages.callbacks) == 1

        self._app.chat_messages.add("first")
        assert json.loads((await first_response).body) == {"message": "first"}
        assert self._app.chat_messages.callbacks == []

        next_response = self.http_client.fetch(self.get_url("/message"))
        for _ in range(100):
            if len(self._app.chat_messages.callbacks) == 1:
                break
            await asyncio.sleep(0.01)
        assert len(self._app.chat_messages.callbacks) == 1
        self._app.chat_messages.add("next")

        assert json.loads((await next_response).body) == {"message": "next"}
        assert self._app.chat_messages.callbacks == []

    def test_template_paths_are_independent_of_working_directory(self):
        response = self.fetch("/")

        assert response.code == 200
        assert b"message" in response.body

    def test_comet_post_rejects_missing_xsrf_token(self):
        response = self.fetch(
            "/message",
            method="POST",
            body=urlencode({"message": "hello"}),
            raise_error=False,
        )

        assert response.code == 403

    def test_comet_post_accepts_rendered_xsrf_token(self):
        token = self._fetch_xsrf_token()
        received = []
        self._app.chat_messages.register_callback(received.append)

        response = self.fetch(
            "/message",
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": f"_xsrf={token}",
            },
            body=urlencode({"_xsrf": token, "message": "  hello  "}),
        )

        assert response.code == 200
        assert received == ["hello"]

    def test_comet_post_accepts_maximum_browser_form_body(self):
        token = self._fetch_xsrf_token()
        message = "\U0001f600" * self.comet.MAX_MESSAGE_LENGTH
        boundary = "TornadoWebSamplesBoundary"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="_xsrf"\r\n\r\n'
            f"{token}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="message"\r\n\r\n'
            f"{message}\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")
        received = []
        self._app.chat_messages.register_callback(received.append)

        assert len(body) < self.comet.MAX_COMET_REQUEST_BODY_SIZE

        response = self.fetch(
            "/message",
            method="POST",
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Cookie": f"_xsrf={token}",
            },
            body=body,
        )

        assert response.code == 200
        assert received == [message]

    def test_comet_post_rejects_oversized_request_body(self):
        received = []
        self._app.chat_messages.register_callback(received.append)

        response = self.fetch(
            "/message",
            method="POST",
            headers={"Content-Type": "application/octet-stream"},
            body=b"x" * (self.comet.MAX_COMET_REQUEST_BODY_SIZE + 1),
            raise_error=False,
        )

        assert response.code == 400
        assert received == []


class TestSocketApplication(AsyncHTTPTestCase):
    def get_app(self):
        self.socket = load_module(
            "socket_runtime_app", "socket_chat/application.py"
        )
        return self.socket.Application(
            max_chat_clients=1,
            max_messages_per_window=1,
            message_rate_window_seconds=60,
        )

    async def _connect(self):
        request = HTTPRequest(
            self.get_url("/message").replace("http://", "ws://", 1),
            headers={"Origin": self.get_url("/").rstrip("/")},
        )
        return await websocket_connect(request)

    @gen_test
    async def test_websocket_capacity_closes_overload_and_reuses_slot(self):
        clients = []
        try:
            first = await self._connect()
            clients.append(first)
            assert len(self._app.chat_clients) == 1

            overloaded = await self._connect()
            clients.append(overloaded)
            assert await overloaded.read_message() is None
            assert overloaded.close_code == 1013
            assert overloaded.close_reason == "Chat capacity reached"
            assert len(self._app.chat_clients) == 1
            await first.write_message(json.dumps({"body": "still connected"}))
            assert await first.read_message() == "still connected"

            first.close()
            for _ in range(100):
                if not self._app.chat_clients:
                    break
                await asyncio.sleep(0.01)
            assert self._app.chat_clients == set()

            replacement = await self._connect()
            clients.append(replacement)
            assert len(self._app.chat_clients) == 1
        finally:
            for client in clients:
                client.close()

    @gen_test
    async def test_websocket_message_rate_limit_closes_offending_client(self):
        client = await self._connect()
        try:
            await client.write_message(json.dumps({"body": "allowed"}))
            assert await client.read_message() == "allowed"

            await client.write_message(json.dumps({"body": "overloaded"}))

            assert await client.read_message() is None
            assert client.close_code == 1008
            assert client.close_reason == "Message rate limit exceeded"
            assert self._app.chat_clients == set()
        finally:
            client.close()
