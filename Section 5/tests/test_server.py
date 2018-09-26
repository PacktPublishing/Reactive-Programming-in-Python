from sys import path
from os.path import dirname, join
path.append(join(dirname(__file__), '..'))
path.append(join(dirname(__file__), '..', 'server'))

import unittest

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.websocket import websocket_connect

from server.server import Server

class ServerTestCase(AsyncHTTPTestCase):
    def __init__(self, *args, **kwargs):
        AsyncHTTPTestCase.__init__(self, *args, **kwargs)
        self.server = Server()

    def get_app(self):
        return self.server._app

    @gen_test
    def test_messages(self):
        def assert_message(message):
            if message[0] != 'message':
                return
            self.assertFalse(self.server.orders.empty(), 'queue of orders should not be empty')

        self.server.messages.subscribe(assert_message)
        self.server.start()
        ws = yield websocket_connect('ws://localhost:8888/exchange')
        self.assertTrue(self.server.orders.empty(), 'queue of orders should be empty')
        ws.write_message('order,007,ABC,buy,100,1.23')

if __name__ == '__main__':
    unittest.main()
