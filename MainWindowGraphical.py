from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QPushButton
from PyQt6.uic import loadUi
from IBInterface import MainIB
from IBAlternative import IBAlternative
import random
import time
import threading
from Constants import *
import traceback


class MainWindow(QMainWindow):
    asset_type_dict = {
        'STK': STOCK,
        'CASH': CURRENCY
    }

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi('MainWindow.ui', self)
        self.ib = MainIB(client_id=random.randint(20, 30))

        self.ib_alternative = IBAlternative(ib=self.ib)

        self.display_positions_btn.clicked.connect(self.display_positions_clicked)
        self.get_positions_btn.clicked.connect(self.start_getting_positions)

        self.positions = None

        self.table_items = {}

    def get_positions_from_ib(self):

        positions = self.ib.get_positions()

        for _ in range(100):

            if len(positions) == 0:
                time.sleep(0.1)
            else:
                break
        self.positions = positions
        self.get_positions_btn.setEnabled(True)
        self.get_positions_btn.setText("Done")

    def start_getting_positions(self):

        self.table.setRowCount(0)

        self.positions = []

        self.get_positions_btn.setText("Getting")

        self.get_positions_btn.setEnabled(False)

        t = threading.Thread(target=self.get_positions_from_ib)
        t.start()

    def buy(self, ticker, asset_type, quantity):

        try:

            print(f'ticker in buy function: {ticker}')

            contract = self.ib.make_contract(ticker, asset_type)

            p = self.ib.get_market_data(
                contract=contract,
                data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE],
                live_data=False
            )

            time.sleep(2)

            price = p.close

            self.ib_alternative.ib_buy(
                ticker=ticker,
                asset_type=asset_type,
                quantity=quantity,
                price=price
            )
        except Exception as error:
            print(f'error: {error}')
            traceback.print_exc()
        return

    def fill_table_dict(self, ticker, position_size, asset_type, long_btn, short_btn, close_btn):

        self.table_items[ticker] = {
            'position_size': position_size,
            'asset_type': asset_type,
            'long_btn': long_btn,
            'short_btn': short_btn,
            'close_btn': close_btn
        }

    def connect_buttons_to_functions(self):

        for ticker in self.table_items.keys():
            self.table_items[ticker]['long_btn'].clicked.connect(lambda x:
                                                                 self.buy(
                                                                     ticker=ticker,
                                                                     asset_type=self.table_items[ticker] \
                                                                         ['asset_type'],
                                                                     quantity=self.table_items[ticker] \
                                                                         ['position_size']
                                                                 )
                                                                 )

    def display_positions_clicked(self):

        row_count = self.table.rowCount()

        for p in self.positions:
            position_type = 'LONG' if float(p.position) > 0 else 'SHORT'
            long_btn = QPushButton()
            long_btn.setText(f'LONG')

            short_btn = QPushButton()
            short_btn.setText('SHORT')
            close_btn = QPushButton()
            close_btn.setText('CLOSE')

            # long_btn.clicked.connect(lambda x: self.buy(
            #     ticker=p.ticker,
            #     asset_type=self.asset_type_dict[p.asset_type],
            #     quantity=float(p.position)
            # ))
            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(p.ticker))
            self.table.setItem(row_count, 1, QTableWidgetItem(p.asset_type))
            self.table.setItem(row_count, 2, QTableWidgetItem(str(p.position)))
            self.table.setItem(row_count, 3, QTableWidgetItem(position_type))
            self.table.setCellWidget(row_count, 4, long_btn)
            self.table.setCellWidget(row_count, 5, short_btn)
            self.table.setCellWidget(row_count, 6, close_btn)

            self.fill_table_dict(
                ticker=p.ticker,
                position_size=p.position,
                asset_type=p.asset_type,
                long_btn=long_btn,
                short_btn=short_btn,
                close_btn=close_btn
            )

            row_count += 1
        self.connect_buttons_to_functions()
        self.get_positions_btn.setText("Get Positions")
