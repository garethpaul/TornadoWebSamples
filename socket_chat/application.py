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
BASE_DIR = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)


def normalize_message(message):
    if not isinstance(message, str):
        return None
    message = message.strip()
    if not message or len(message) > MAX_MESSAGE_LENGTH:
        return None
    return message


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
        self.application.chat_clients.add(self)

    def on_close(self):
        """
        Post a message here
        """
        self.application.chat_clients.discard(self)

    def on_message(self, message):
        """
        Message received
        """
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
                cb.write_message(body)
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

    def __init__(self):
        self.chat_clients = set()
        handlers = [
            (r'/', MainHandler),
            (r'/message', MessageHandler),
        ]

        # app settings
        settings = {
            'template_path' : str(BASE_DIR / 'templates'),
            'static_path' : str(BASE_DIR / 'static'),
            }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000, address='127.0.0.1')
    autoreload.start()
    tornado.ioloop.IOLoop.current().start()
