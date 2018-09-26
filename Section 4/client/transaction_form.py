from PyQt5.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QWidget

from rx.subjects import Subject

from client.transaction_validator import TransactionValidator

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
            self.set_error_label(*error)
        self._validator.on_error(invalid_field)

        def enable_order_submission():
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
