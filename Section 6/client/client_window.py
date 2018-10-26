from PyQt5.QtWidgets import QWidget, QGridLayout

from rx.subjects import Subject

from client.transaction_form import TransactionForm
from client.stock_overview_table import StockOverviewTable

class ClientWindow(QWidget):
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
        self.setWindowTitle('client: stock exchange')

    def get_orders(self):
        return self._form.orders_stream
