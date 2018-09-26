import asyncio
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
    def make_say_hello(client, i):
        def say_hello():
            client.write_message('hello world #{}!'.format(i))
        def schedule_say_hello(conn):
            #print('???')
            Observable.interval(choice([300, 500, 1000, 2000, 3000]), scheduler=scheduler).subscribe(lambda value: say_hello())
        return schedule_say_hello

    for i in range(10):
        client = Client()
        client.messages.subscribe(lambda message: print(message))
        #client.opened.subscribe(lambda conn: print('connection opened to server'))
        
        client.messages.filter(lambda msg: msg.starts_with('update'))
        client.opened.subscribe(lambda conn: print('subscriber A'))
        client.opened.subscribe(lambda conn: print('subscriber B'))
        client.opened.subscribe(lambda conn: print('subscriber C'))

        client.opened.subscribe(make_say_hello(client, i))
        client.connect()
    IOLoop.current().start()
