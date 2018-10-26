import asyncio
import datetime
from random import choice

from rx import Observable
from rx.subjects import Subject
from rx.concurrency import IOLoopScheduler

from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect

class Client:
    def __init__(self, host='localhost', port='8888'):
        self._url = 'ws://{}:{}/exchange'.format(host, port)
        self.conn = None
        self.opened = Subject()
        self.messages = Subject()
        # self.messages.subscribe(lambda msg: print('received: {}'.format(msg)))

    def connect(self):
        def on_connect(conn):
            print('on_connect')
            self.conn = conn
            self.opened.on_next(conn)
            self.opened.on_completed()
            self.opened.dispose()

        def on_message_callback(message):
            # print('on_message_callback')
            self.messages.on_next(message)

        print('connect to server')
        future = websocket_connect(
            self._url,
            on_message_callback=on_message_callback,
        )
        Observable.from_future(future).subscribe(on_connect)

    def write_message(self, message):
        self.conn.write_message(message)

if __name__ == '__main__':
    scheduler = IOLoopScheduler(IOLoop.current())

    def make_say_hello(client, client_id):
        def say_hello():
            print('{} client #{} is sending orders'.format(
                datetime.datetime.now(), client_id))
            symbols = ['ABC', 'DEF', 'GHI', 'A', 'GS', 'GO']
            quantities = [90, 100, 110]
            prices = [1.20, 1.21, 1.22, 1.23, 1.24, 1.25]
            client.write_message(
                'order,{},{},buy,{},{}'.format(client_id, choice(symbols), choice(quantities), choice(prices)))
            client.write_message(
                'order,{},{},sell,{},{}'.format(client_id, choice(symbols), choice(quantities), choice(prices)))

        def schedule_say_hello(conn):
            sleep = 5000
            Observable \
                .interval(sleep, scheduler=scheduler) \
                .subscribe(lambda value: say_hello())
        return schedule_say_hello

    clients = []
    for client_id in range(10):
        client = Client(port='9999')
        client.opened.subscribe(make_say_hello(client, client_id))
        clients.append(client)

    for client in clients:
        client.connect()
    IOLoop.current().start()
