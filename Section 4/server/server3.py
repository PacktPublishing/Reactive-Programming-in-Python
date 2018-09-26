from rx.concurrency import IOLoopScheduler

from tornado.ioloop import IOLoop
from tornado.queues import PriorityQueue, QueueEmpty
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

from rx import Observable
from rx.subjects import Subject

from order import Order

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
            self.orders = PriorityQueue()
            self.posted_orders = []
            self.fulfilled_orders = []
            self.messages = Subject()
            only_messages = self.messages \
                .filter(lambda msg: msg[0] == 'message') \
                .map(lambda msg: msg[1].split(',')) \
                .publish()
            def queue_order(msg):
                self.orders.put(Order.from_list(msg))
            only_messages \
                .filter(lambda msg: msg[0] == 'order') \
                .map(lambda msg: msg[1:]) \
                .subscribe(queue_order)
            def process_order(time):
                try:
                    order = self.orders.get_nowait()
                    print('processing order: {} [{}]'.format(
                        order, order.timestamp))
                    matching = None
                    for posted in self.posted_orders:
                        if posted.matches(order):
                            matching = posted
                            break

                    if matching is None:
                        self.posted_orders.append(order)
                        print('could not find match, posted order count is {}'.format(len(self.posted_orders)))
                    else:
                        self.posted_orders.remove(posted)
                        self.fulfilled_orders.append(posted)
                        self.fulfilled_orders.append(order)
                        print('order fulfilled: {}'.format(order))
                        print('fulfilled by: {}'.format(posted))
                except QueueEmpty:
                    pass
            Observable.interval(100, scheduler=scheduler).subscribe(process_order)
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
    Server().messages \
            .filter(lambda msg: msg == 'opened') \
            .subscribe(lambda msg: print('Connection has been opened'))
    Server().start()
    IOLoop.current().start()
