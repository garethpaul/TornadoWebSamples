import asyncio
import importlib.util
import json
from pathlib import Path

from tornado.testing import AsyncHTTPTestCase, gen_test


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

    def test_template_paths_are_independent_of_working_directory(self):
        response = self.fetch("/")

        assert response.code == 200
        assert b"message" in response.body
