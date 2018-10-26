import sys
import random
import datetime
import asyncio
from threading import Thread

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from tornado.ioloop import IOLoop

from rx import Observable
from rx.subjects import Subject
from rx.concurrency import QtScheduler, AsyncIOScheduler

from client.client import Client
from client.client_window import ClientWindow

import utils

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scheduler = QtScheduler(QtCore)
    stock_prices = Subject()
    client = Client(port='9999')

    loop = asyncio.new_event_loop()
    asyncio_scheduler = AsyncIOScheduler(loop)

    def run_client():
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().call_soon(
            utils.run_client_websocket, client, stock_prices)
        asyncio.get_event_loop().run_forever()

    thread = Thread(target=run_client, daemon=True)
    thread.start()

    client_window = ClientWindow(stock_prices_stream=stock_prices)

    def send_order(order):
        stock_order = {
            'stock_symbol': order['symbol'],
            'price': order['price'],
            'direction': 'buy',
            'quantity': 1,
        }
        utils.write_order(client, stock_order)

    client_window.get_orders() \
        .filter(utils.order_is_valid) \
        .subscribe(send_order)

    client_window.show()
    sys.exit(app.exec_())
