import asyncio
from collections import deque
import time
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.websocket
import tornado.escape
from tornado import autoreload
import logging
from pathlib import Path


MAX_MESSAGE_LENGTH = 500
MAX_WEBSOCKET_FRAME_SIZE = 4096
MAX_WEBSOCKET_CLIENTS = 100
WEBSOCKET_OVERLOAD_CLOSE_CODE = 1013
WEBSOCKET_OVERLOAD_CLOSE_REASON = 'Chat capacity reached'
MAX_WEBSOCKET_MESSAGES_PER_WINDOW = 10
WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS = 1
WEBSOCKET_RATE_LIMIT_CLOSE_CODE = 1008
WEBSOCKET_RATE_LIMIT_CLOSE_REASON = 'Message rate limit exceeded'
BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def normalize_message(message):
    if not isinstance(message, str):
        return None
    message = message.strip()
    if not message or len(message) > MAX_MESSAGE_LENGTH:
        return None
    return message


class MessageRateLimiter(object):
    def __init__(self, max_messages, window_seconds, clock=time.monotonic):
        if max_messages < 1:
            raise ValueError('max_messages must be positive')
        if window_seconds <= 0:
            raise ValueError('window_seconds must be positive')
        self.max_messages = max_messages
        self.window_seconds = window_seconds
        self.clock = clock
        self.timestamps = deque()

    def allow(self):
        now = self.clock()
        cutoff = now - self.window_seconds
        while self.timestamps and self.timestamps[0] <= cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_messages:
            return False
        self.timestamps.append(now)
        return True


class MessageHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        host = self.request.headers.get('Host')
        if not origin or not host:
            return False

        normalized_origin = origin.lower().rstrip('/')
        normalized_host = host.lower()
        return normalized_origin in (
            'http://' + normalized_host,
            'https://' + normalized_host,
        )

    def open(self):
        self._message_rate_limiter = MessageRateLimiter(
            self.application.max_messages_per_window,
            self.application.message_rate_window_seconds,
        )
        if not self.application.register_chat_client(self):
            self.close(
                code=WEBSOCKET_OVERLOAD_CLOSE_CODE,
                reason=WEBSOCKET_OVERLOAD_CLOSE_REASON,
            )

    def on_close(self):
        """
        Post a message here
        """
        self.application.chat_clients.discard(self)

    def _finish_delivery(self, client, delivery):
        try:
            delivery.result()
        except (asyncio.CancelledError, Exception):
            logger.exception("Could not deliver websocket chat message")
            self.application.chat_clients.discard(client)

    def on_message(self, message):
        """
        Message received
        """
        if not hasattr(self, '_message_rate_limiter'):
            self._message_rate_limiter = MessageRateLimiter(
                getattr(
                    self.application,
                    'max_messages_per_window',
                    MAX_WEBSOCKET_MESSAGES_PER_WINDOW,
                ),
                getattr(
                    self.application,
                    'message_rate_window_seconds',
                    WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS,
                ),
            )
        if not self._message_rate_limiter.allow():
            self.application.chat_clients.discard(self)
            self.close(
                code=WEBSOCKET_RATE_LIMIT_CLOSE_CODE,
                reason=WEBSOCKET_RATE_LIMIT_CLOSE_REASON,
            )
            return

        try:
            parsed = tornado.escape.json_decode(message)
        except ValueError:
            self.close(code=1003, reason='Invalid chat message')
            return

        body = parsed.get('body') if isinstance(parsed, dict) else None
        body = normalize_message(body)
        if body is None:
            self.close(code=1003, reason='Invalid chat message')
            return

        for cb in list(self.application.chat_clients):
            try:
                delivery = cb.write_message(body)
                if delivery is not None:
                    delivery.add_done_callback(
                        lambda future, client=cb: self._finish_delivery(
                            client, future))
            except Exception:
                logger.exception("Could not deliver websocket chat message")
                self.application.chat_clients.discard(cb)


class MainHandler(tornado.web.RequestHandler):
    """
    The main handler
    """

    def get(self, *args, **kwargs):
        return self.render('index.html')


class Application(tornado.web.Application):
    """
    This is out application class where we can be specific about  its
    configuration etc.
    """

    def __init__(
            self,
            max_chat_clients=MAX_WEBSOCKET_CLIENTS,
            max_messages_per_window=MAX_WEBSOCKET_MESSAGES_PER_WINDOW,
            message_rate_window_seconds=WEBSOCKET_MESSAGE_RATE_WINDOW_SECONDS):
        self.chat_clients = set()
        self.max_chat_clients = max_chat_clients
        self.max_messages_per_window = max_messages_per_window
        self.message_rate_window_seconds = message_rate_window_seconds
        handlers = [
            (r'/', MainHandler),
            (r'/message', MessageHandler),
        ]

        # app settings
        settings = {
            'template_path' : str(BASE_DIR / 'templates'),
            'static_path' : str(BASE_DIR / 'static'),
            'websocket_max_message_size' : MAX_WEBSOCKET_FRAME_SIZE,
            }
        tornado.web.Application.__init__(self, handlers, **settings)

    def register_chat_client(self, client):
        if client in self.chat_clients:
            return True
        if len(self.chat_clients) >= self.max_chat_clients:
            return False
        self.chat_clients.add(client)
        return True


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000, address='127.0.0.1')
    autoreload.start()
    tornado.ioloop.IOLoop.current().start()
