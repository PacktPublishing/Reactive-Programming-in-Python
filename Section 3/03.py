import sys
import random
import re

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QGridLayout, QLabel, QLineEdit, QFormLayout

from rx import Observable
from rx.subjects import Subject
from rx.concurrency import QtScheduler

class TransactionValidator:
    def __init__(self):
        self._error_stream = Subject()
        self._price_stream = Subject()
        self._symbol_stream = Subject()
        self.latest_valid_order = None

    def next_error(self, field, error_text):
        self._error_stream.on_next([field, error_text])

    def next_price(self, value):
        if len(value) == 0:
            self.next_error('price', 'cannot be blank')
        else:
            try:
                price = float(value)
                if price < 0.01:
                    self.next_error('price', 'must be greater than 0.00')
                else:
                    print('trace: {}'.format(price))
                    self._price_stream.on_next(price)
            except ValueError:
                if len(re.sub('[a-zA-Z ]', '', value)) == 0:
                    self.next_error('price', 'must be a number')

    def next_symbol(self, value):
        if len(value) == 0 or len(re.sub('[0-9 ]', '', value)) == 0:
            self.next_error('symbol', 'cannot be blank')
        else:
            self._symbol_stream.on_next(value)

    def on_error(self, func):
        self._error_stream.subscribe(func)

    def on_valid_order(self, func):
        def store_order_and_send_to_subscriber(order):
            self.latest_valid_order = order
            func()

        Observable.combine_latest(
            self._symbol_stream,
            self._price_stream,
            lambda symbol, price: { 'symbol': symbol, 'price': price }
        ).subscribe(store_order_and_send_to_subscriber)

class TransactionForm(QWidget):
    def __init__(self, *args, **kwargs):
        self.orders_stream = Subject()
        self._validator = TransactionValidator()
        QWidget.__init__(self, *args, **kwargs)
        self._setup_form()
        self._connect_events()
        self._subscribe_to_streams()

    def _setup_form(self):
        self._symbol_input = QLineEdit()
        self._symbol_error_label = QLabel()
        self._price_input = QLineEdit()
        self._price_error_label = QLabel()
        self._ok_button = QPushButton('Post Order')
        self._layout = QFormLayout(self)
        self._layout.addRow('Symbol:', self._symbol_input)
        self._layout.addRow(self._symbol_error_label)
        self._layout.addRow('Price:', self._price_input)
        self._layout.addRow(self._price_error_label)
        self._layout.addRow(self._ok_button)
        self._clear_form()

    def _connect_events(self):
        self._ok_button.clicked.connect(self.submit_order)
        self._symbol_input.textChanged.connect(self._symbol_text_changed)
        self._price_input.textChanged.connect(self._price_text_changed)

    def _subscribe_to_streams(self):
        def invalid_field(error):
            print(error)
            self.set_error_label(*error)
        self._validator.on_error(invalid_field)

        def enable_order_submission():
            print('order submission button enabled')
            self._ok_button.setEnabled(True)
        self._validator.on_valid_order(enable_order_submission)

    def set_error_label(self, field, text):
        label = '_{}_error_label'.format(field)
        getattr(self, label).setText(text)

    def _clear_form(self):
        for widget_name in ['symbol_input', 'symbol_error_label', 'price_input', 'price_error_label']:
            widget = '_{}'.format(widget_name)
            getattr(self, widget).setText('')
        self._ok_button.setEnabled(False)

    def submit_order(self):
        self.orders_stream.on_next(self._validator.latest_valid_order)
        self._clear_form()

    def _symbol_text_changed(self):
        self._symbol_error_label.setText('')
        value = self._symbol_input.text()
        self._validator.next_symbol(value)

    def _price_text_changed(self):
        self._price_error_label.setText('')
        price_string = self._price_input.text()
        self._validator.next_price(price_string)

class StockOverviewTable(QTableWidget):
    def __init__(self, *args, **kwargs):
        stock_prices_stream = kwargs.pop('stock_prices_stream')
        QTableWidget.__init__(self, *args, **kwargs)
        self.setRowCount(0)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Symbol', 'Name', 'Buy Price', 'Sell Price'])
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 100)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(True)
        stock_prices_stream.subscribe(self._create_or_update_stock_row)

    def _find_matching_row_index(self, stock_row):
        matches = self.findItems(stock_row[0], QtCore.Qt.MatchExactly)
        if len(matches) == 0:
            self.setRowCount(self.rowCount() + 1)
            return self.rowCount() - 1
        return self.indexFromItem(matches[0]).row()

    def _create_or_update_stock_row(self, stock_row):
        row = self._find_matching_row_index(stock_row)

        column_index = 0
        for column in stock_row:
            self.setItem(row, column_index, QTableWidgetItem(str(column)))
            column_index += 1

class HelloWorld(QWidget):
    def __init__(self, *args, **kwargs):
        stock_prices_stream = kwargs.pop('stock_prices_stream')
        QWidget.__init__(self, *args, **kwargs)
        self.events = Subject()
        self._setup_window()
        self._layout = QGridLayout(self)
        self._overview_table = StockOverviewTable(stock_prices_stream=stock_prices_stream)
        self._form = TransactionForm()
        self._layout.addWidget(self._overview_table, 0, 0)
        self._layout.addWidget(self._form, 0, 2)
        self._layout.setColumnStretch(0, 2)

    def _setup_window(self):
        self.resize(640, 320)
        self.move(350, 200)
        self.setWindowTitle('hello world')

    def get_orders(self):
        return self._form.orders_stream

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
    print('Order received: {}'.format(order))
    if order['symbol'] != '' and order['price'] >= 0.01:
        return True
    return False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    scheduler = QtScheduler(QtCore)
    stock_prices = Observable.interval(REFRESH_STOCK_INTERVAL, scheduler) \
        .map(random_stock) \
        .publish()
    hello_world = HelloWorld(stock_prices_stream=stock_prices)
    hello_world.get_orders() \
               .filter(order_is_valid) \
               .subscribe(lambda x: print(x), lambda x: print('error'))
    stock_prices.connect()
    hello_world.show()
    sys.exit(app.exec_())
