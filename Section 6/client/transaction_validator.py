import re

from rx import Observable
from rx.subjects import Subject

class TransactionValidator:
    def __init__(self):
        self._error_stream = Subject()
        self._price_stream = Subject()
        self._symbol_stream = Subject()
        self.latest_valid_order = None

    def next_error(self, field, error_text):
        self._error_stream.on_next([field, error_text])

    # We're going to check if the price text has changed to a valid
    # value. If it is an empty string or not a number that's greater
    # than 0.0 we're going to emit an error in the error stream. If
    # it's valid, we will emit the value to the price stream.
    def next_price(self, value):
        if len(value) == 0:
            self.next_error('price', 'cannot be blank')
        else:
            try:
                price = float(value)
                if price < 0.01:
                    self.next_error('price', 'must be greater than 0.00')
                else:
                    self._price_stream.on_next(price)
            except ValueError:
                if len(re.sub('[a-zA-Z ]', '', value)) == 0:
                    self.next_error('price', 'must be a number')

    # We're going to check if the symbol text has changed.  It's a
    # simple check, we want to make sure it isn't an empty string. If
    # it's valid, we will emit the value on the symbol stream. If it's
    # invalid, we'll emit the error on the error stream.
    def next_symbol(self, value):
        if len(value) == 0 or len(re.sub('[0-9 ]', '', value)) == 0:
            self.next_error('symbol', 'cannot be blank')
        else:
            self._symbol_stream.on_next(value)

    def on_error(self, func):
        self._error_stream.subscribe(func)

    def on_valid_order(self, func):
        # Combine latest will emit items when any of the observables
        # have an item to emit. We want the latest valid values that
        # the user has entered in the symbol and price input
        # boxes. When we have that, we can enable the "submit order"
        # button. The form inputs and buttons are manipulated through
        # the subscription function that was passed in.
        def store_order_and_send_to_subscriber(order):
            self.latest_valid_order = order
            func(order)

        Observable.combine_latest(
            self._symbol_stream,
            self._price_stream,
            lambda symbol, price: { 'symbol': symbol, 'price': price }
        ).subscribe(store_order_and_send_to_subscriber)
