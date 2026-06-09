import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado import autoreload
import json


MAX_MESSAGE_LENGTH = 500


def normalize_message(message):
    if not isinstance(message, str):
        return None
    message = message.strip()
    if not message or len(message) > MAX_MESSAGE_LENGTH:
        return None
    return message


class Messages(object):
    """
    This is a pretty straight forward messages class that will handle the
    callbacks waiting to hear new messages
    """

    def __init__(self):
        self.callbacks = []

    def add(self, message):
        """
        For every message added, all the callbacks are fired. These callbacks
        are requests waiting to hear for changes
        """
        for cb in self.callbacks:
            cb(message)
        self.callbacks = [] # reset the callbacks

    def register_callback(self, callback):
        """
        Register a callback for when messages are added
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def remove_callback(self, callback):
        """
        Remove a waiting callback when its request disconnects
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)



class MessageHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        """
        Get the latest messages
        """
        self._message_callback = self.async_callback(self.on_message)
        self.application.chat_messages.register_callback(
            self._message_callback)

    def on_connection_close(self):
        """
        Remove abandoned long-poll callbacks
        """
        callback = getattr(self, '_message_callback', None)
        if callback is not None:
            self.application.chat_messages.remove_callback(callback)
            self._message_callback = None

    def post(self, *args, **kwargs):
        """
        Post a message here
        """
        message = normalize_message(self.get_argument('message', ''))
        if message is None:
            self.set_status(400)
            return

        self.application.chat_messages.add(message)

    def on_message(self, message):
        """
        We'll json the message out
        """
        self._message_callback = None
        self.write(json.dumps({'message':message}))
        self.finish()


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
        self.chat_messages = Messages()

        handlers = [
            (r'/', MainHandler),
            (r'/message', MessageHandler),
        ]

        # app settings
        settings = {
            'template_path' : 'templates',
            'static_path' : 'static',
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    ioloop = tornado.ioloop.IOLoop.instance()
    autoreload.start(ioloop)
    ioloop.start()
