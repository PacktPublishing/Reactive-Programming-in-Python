import unittest
from sys import path
from os.path import dirname, join
path.append(join(dirname(__file__), '..'))

from PyQt5.QtWidgets import QApplication

from client.transaction_form import TransactionForm

class TestTransactionForm(unittest.TestCase):
    def test_symbol_input(self):
        form = TransactionForm()
        form._validator._symbol_stream.subscribe(
            lambda symbol: self.assertEqual(symbol, 'ABC'))
        form._symbol_input.setText('ABC')

    def test_price_input(self):
        form = TransactionForm()
        form._validator._price_stream.subscribe(
            lambda price: self.assertEqual(price, 12.34))
        form._price_input.setText('12.34')

    def test_form_valid_order_entered(self):
        form = TransactionForm()
        def assert_valid_order(order):
            print(order)
            return order['symbol'] == 'ABC' and order['price'] == 12.34
        form._validator.on_valid_order(assert_valid_order)
        self.assertFalse(form._ok_button.isEnabled())
        form._symbol_input.setText('ABC')
        form._price_input.setText('12.34')
        self.assertTrue(form._ok_button.isEnabled())

        form.orders_stream.subscribe(assert_valid_order)
        form._ok_button.click()

if __name__ == '__main__':
    app = QApplication([])
    unittest.main()
