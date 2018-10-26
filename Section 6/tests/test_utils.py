from sys import path
from os.path import dirname, join
path.append(join(dirname(__file__), '..'))

from unittest import main
from unittest import TestCase

from rx import Observable
from rx.subjects import Subject
from rx.testing import TestScheduler, ReactiveTest

import utils

class OrderIsValidTestCase(TestCase):
    INVALID_ORDERS = (
        ('', None),
        (None, -1),
        ('ABC', -1),
        ('ABC', 0),
        ('ABC', 0.001),
        ('   ', 1),
    )

    VALID_ORDERS = (
        ('ABC', 0.01),
        ('A', 99999.99),
        ('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 100.00),
        ('DEF', 0.010),
        ('GHI', 0.1),
    )

    def test_empty_order(self):
        self.assertFalse(utils.order_is_valid({}))

    def _test_order(self, assert_func, msg, test_case):
        order = { 'symbol': test_case[0], 'price': test_case[1] }
        assert_func(
            utils.order_is_valid(order),
            'Order {} should be {}'.format(order, msg)
        )

    def test_invalid_orders(self):
        for test_case in self.INVALID_ORDERS:
            self._test_order(self.assertFalse, 'invalid', test_case)

    def test_valid_orders(self):
        for test_case in self.VALID_ORDERS:
            self._test_order(self.assertTrue, 'valid', test_case)

class ParseStockFromMsgTestCase(TestCase):
    def test_unfulfilled_order(self):
        msg = 'posted: 32: sell ABC 199 @ $1.23'
        self.assertEqual(utils.parse_stock_from_msg(msg), {
            'direction': 'sell',
            'stock_symbol': 'ABC',
            'quantity': 199,
            'price': 1.23,
            'fulfilled': False,
            'fulfilled_by': None,
        })

    def test_fulfilled_order(self):
        msg = 'fulfilled: 32: sell ABC 199 @ $1.23'
        self.assertEqual(utils.parse_stock_from_msg(msg), {
            'direction': 'sell',
            'stock_symbol': 'ABC',
            'quantity': 199,
            'price': 1.23,
            'fulfilled': True,
            'fulfilled_by': '32',
        })

class WriteOrder(TestCase):
    class MockClient:
        def __init__(self):
            self.messages_written = []

        def write_message(self, msg):
            self.messages_written.append(msg)

    def test_valid_orders(self):
        mock_client = self.MockClient()
        utils.write_order(mock_client, {
            'direction': 'sell',
            'stock_symbol': 'ABC',
            'quantity': 199,
            'price': 1.23,
        })
        utils.write_order(mock_client, {
            'direction': 'buy',
            'stock_symbol': 'DEF',
            'quantity': 2,
            'price': 1.23,
        })
        utils.write_order(mock_client, {
            'direction': 'buy',
            'stock_symbol': 'ABC',
            'quantity': 1,
            'price': 1.20,
        })
        self.assertEqual(mock_client.messages_written, [
            'order,0,ABC,sell,199,1.23',
            'order,0,DEF,buy,2,1.23',
            'order,0,ABC,buy,1,1.2',
        ])

class AggregateStockOrdersFromMessages(TestCase):
    def test_interval(self):
        scheduler = TestScheduler()
        on_next = ReactiveTest.on_next
        self.messages = scheduler.create_hot_observable(
            on_next(10, 'posted: 32: sell ABC 199 @ $1.23'),
            on_next(11, 'fulfilled: 32: sell ABC 199 @ $1.23'),
            on_next(101, 'posted: 32: buy ABC 199 @ $1.23'),
            on_next(102, 'fulfilled: 32: buy ABC 199 @ $1.23'),
            ReactiveTest.on_completed(750),
        )
        self.results = []

        def create(scheduler, state):
            self.aggregate = utils.aggregate_stock_orders_from_messages(self.messages)
        def subscribe(scheduler, state):
            self.subscription = self.aggregate.subscribe(lambda value: self.results.append(value))
        def dispose(scheduler, state):
            self.subscription.dispose()

        scheduler.schedule_absolute(1, create)
        scheduler.schedule_absolute(2, subscribe)
        scheduler.schedule_absolute(1000, dispose)

        scheduler.start().messages
        self.results

class FindPrices(TestCase):
    def test_no_orders(self):
        self.assertEqual(utils.find_prices([]), {})

    def test_one_stock(self):
        stock_symbol = 'ABC'
        sell_price = 1.21
        buy_price = 1.24
        orders = [
            {
                'direction': 'sell',
                'stock_symbol': stock_symbol,
                'quantity': 1,
                'price': sell_price,
                'fulfilled': False,
                'fulfilled_by': None,
            },
            {
                'direction': 'buy',
                'stock_symbol': stock_symbol,
                'quantity': 1,
                'price': buy_price,
                'fulfilled': False,
                'fulfilled_by': None,
            }
        ]
        self.assertEqual(utils.find_prices(orders), {
            stock_symbol: (buy_price, sell_price) })

    def test_one_stock(self):
        stock_symbol_a = 'ABC'
        stock_symbol_b = 'DEF'
        sell_price = 1.21
        buy_price = 1.24
        orders = [
            {
                'direction': 'sell',
                'stock_symbol': stock_symbol_a,
                'quantity': 1,
                'price': sell_price,
                'fulfilled': False,
                'fulfilled_by': None,
            },
            {
                'direction': 'buy',
                'stock_symbol': stock_symbol_b,
                'quantity': 1,
                'price': buy_price,
                'fulfilled': False,
                'fulfilled_by': None,
            }
        ]
        self.assertEqual(utils.find_prices(orders), {
            stock_symbol_a: (0, sell_price),
            stock_symbol_b: (buy_price, 0),
        })

class FoldPriceOfFilteredOrders(TestCase):
    def test_only_sell_orders(self):
        orders = [
            {
                'direction': 'sell',
                'stock_symbol': 'ABC',
                'quantity': 1,
                'price': 1.20,
                'fulfilled': False,
                'fulfilled_by': None,
            }
        ]
        self.assertEqual(utils.filter_orders('buy', orders), [])
        self.assertEqual(utils.filter_orders('sell', orders), orders)
        self.assertEqual(
            utils.fold_price_of_filtered_orders(max, 'buy', orders), 0.0,
            'max price of buy orders should be 0.0')
        self.assertEqual(
            utils.fold_price_of_filtered_orders(min, 'sell', orders, 1.5), 1.20,
            'min price of sell orders should be 1.5')

    def test_only_buy_orders(self):
        orders = [
            {
                'direction': 'buy',
                'stock_symbol': 'ABC',
                'quantity': 1,
                'price': 1.20,
                'fulfilled': False,
                'fulfilled_by': None,
            }
        ]
        self.assertEqual(utils.filter_orders('buy', orders), orders)
        self.assertEqual(utils.filter_orders('sell', orders), [])
        self.assertEqual(
            utils.fold_price_of_filtered_orders(max, 'buy', orders), 1.2,
            'max price of buy orders should be 1.2')
        self.assertEqual(
            utils.fold_price_of_filtered_orders(min, 'sell', orders, 1.5), 1.5,
            'min price of sell orders should be 1.5')

if __name__ == '__main__':
    main()
