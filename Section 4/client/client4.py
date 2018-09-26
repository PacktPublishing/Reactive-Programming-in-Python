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

    def connect(self):
        def on_connect(conn):
            self.conn = conn
            self.opened.on_next(conn)
            self.opened.on_completed()
            self.opened.dispose()

        def on_message_callback(message):
            self.messages.on_next(message)

        future = websocket_connect(
            self._url,
            on_message_callback=on_message_callback
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
            client.write_message(
                'order,{},ABC,buy,100,1.23'.format(client_id))
            client.write_message(
                'order,{},ABC,sell,110,1.23'.format(client_id))

        def schedule_say_hello(conn):
            sleep = choice([500, 600, 700])
            Observable \
                .interval(sleep, scheduler=scheduler) \
                .subscribe(lambda value: say_hello())
        return schedule_say_hello

    clients = []
    for client_id in range(10):
        client = Client()
        client.messages.subscribe(lambda message: print(message))
        client.opened.subscribe(make_say_hello(client, client_id))
        clients.append(client)

    for client in clients:
        client.connect()
    IOLoop.current().start()
