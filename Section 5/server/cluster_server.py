from rx.concurrency import IOLoopScheduler

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler, websocket_connect

from rx import Observable
from rx.subjects import Subject

class ExchangeHandler(WebSocketHandler):
    def open(self):
        print('server open')
        ClusterServer().messages.on_next(['opened', self.request])

    def on_message(self, message):
        print('server: {}'.format(message))
        ClusterServer().messages.on_next(['message', message])

    def on_close(self):
        print('server closed')
        ClusterServer().messages.on_next(['closed', self.request])

class ClusterServer:
    class Instance:
        def __init__(self):
            scheduler = IOLoopScheduler(IOLoop.current())
            self._app = Application([
                (r'/exchange', ExchangeHandler),
            ])

            self._servers = [
                ['localhost', '8888'],
                ['localhost', '7777'],
            ]
            self._current_server = 0

            self.messages = Subject()

            def passthrough_to_matching_server(msg):
                if self.matching_server_connection is None:
                    print('server is DOWN')
                    return
                self.matching_server_connection.write_message(msg)

            self.only_messages = self.messages \
                .filter(lambda msg: msg[0] == 'message') \
                .map(lambda msg: msg[1]) \
                .subscribe(passthrough_to_matching_server)

        def connect_to_server(self, host, port):
            def on_connect(conn):
                self.matching_server_connection = conn
                print('Connected to matching server')

            def on_message_callback(message):
                if message is None:
                    self.matching_server_connection = None
                    self.connect_to_next_server()
                else:
                    self.message.on_next(message)

            future = websocket_connect(
                'ws://{}:{}/exchange'.format(host, port),
                on_message_callback=on_message_callback
            )
            Observable.from_future(future).subscribe(
                on_connect,
                lambda error: self.connect_to_next_server()
            )

        def connect_to_next_server(self):
            print('Could not connect to server, finding next server')
            if self._current_server == len(self._servers) - 1:
                self._current_server = 0
            else:
                self._current_server += 1
            self.connect_to_server(*self._servers[self._current_server])

        def start(self):
            self.connect_to_server(*self._servers[self._current_server])
            print('Starting transaction server on port 9999')
            self._app.listen(9999)

    instance = None

    def __init__(self):
        cls = self.__class__
        if cls.instance is None:
            cls.instance = cls.Instance()

    def __getattr__(self, name):
        return getattr(self.instance, name)

if __name__ == '__main__':
    ClusterServer().messages \
            .filter(lambda msg: msg == 'opened') \
            .subscribe(lambda msg: print('Connection has been opened'))
    ClusterServer().start()
    IOLoop.current().start()
