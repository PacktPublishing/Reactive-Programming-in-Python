from rx.concurrency import IOLoopScheduler

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

from rx import Observable
from rx.subjects import Subject

class MainHandler(RequestHandler):
    def get(self):
        self.write('Hello Stock Exchange!\n')

class ExchangeHandler(WebSocketHandler):
    def open(self):
        Server().messages.on_next(['opened', self.request])

    def on_message(self, message):
        Server().messages.on_next(['message', message])

    def on_close(self):
        Server().messages.on_next(['closed', self.request])

class Server:
    class __Server:
        def __init__(self):
            scheduler = IOLoopScheduler(IOLoop.current())
            self._app = Application([
                (r'/exchange', ExchangeHandler),
                (r'/', MainHandler),
            ])
            self.messages = Subject()
            only_messages = self.messages.filter(lambda msg: msg[0] == 'message').map(lambda msg: msg[1]).publish()
            only_messages.subscribe(lambda msg: print(msg))
            only_messages.connect()

        def start(self):
            self._app.listen(8888)

    instance = None

    def __init__(self):
        if Server.instance is None:
            Server.instance = Server.__Server()

    def __getattr__(self, name):
        return getattr(self.instance, name)

if __name__ == '__main__':
    Server().messages.subscribe(lambda msg: print('Received: {}'.format(msg)))
    Server().messages.filter(lambda msg: msg == 'opened').subscribe(lambda msg: print('Connection has been opened'))
    Server().start()
    IOLoop.current().start()
