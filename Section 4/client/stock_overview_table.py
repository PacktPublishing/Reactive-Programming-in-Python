from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

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
