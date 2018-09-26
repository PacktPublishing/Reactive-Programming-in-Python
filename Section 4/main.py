import sys
import random

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from rx import Observable
from rx.subjects import Subject
from rx.concurrency import QtScheduler

from client.client_window import ClientWindow

REFRESH_STOCK_INTERVAL = 100

def random_stock(x):
    symbol_names = [
        ['ABC', 'Abc Manufacturing'],
        ['DEF', 'Desert Inc.'],
        ['GHI', 'Ghi Ghi Inc.'],
        ['A', 'A Plus Consulting'],
        ['GS', 'Great Security Inc'],
        ['GO', 'Go Go Consulting'],
    ]
    stock = random.choice(symbol_names)
    return [
        stock[0],
        stock[1],
        round(random.uniform(21, 22), 2),
        round(random.uniform(20, 21), 2)
    ]

def order_is_valid(order):
    if order['symbol'] != '' and order['price'] >= 0.01:
        return True
    return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scheduler = QtScheduler(QtCore)
    stock_prices = Observable.interval(REFRESH_STOCK_INTERVAL, scheduler) \
        .map(random_stock) \
        .publish()
    client_window = ClientWindow(stock_prices_stream=stock_prices)
    client_window.get_orders() \
               .filter(order_is_valid) \
               .subscribe(lambda x: print(x), lambda x: print('error'))
    stock_prices.connect()
    client_window.show()
    sys.exit(app.exec_())
