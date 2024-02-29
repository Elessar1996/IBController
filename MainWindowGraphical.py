from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QPushButton
from PyQt6.uic import loadUi
from IBInterface import MainIB
from IBAlternative import IBAlternative
import random
import time
import threading
from Constants import *
import traceback
import subprocess
import os
import signal

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

        self.table.itemClicked.connect(self.item_clicked)

        self.selected_row = None

        self.buy_btn.clicked.connect(self.buy_clicked)

        self.sell_btn.clicked.connect(self.sell_clicked)

        self.close_btn.clicked.connect(self.close_position)

        self.ngrok_btn.clicked.connect(self.start_running_ngrok)

        self.stop_ngrok_btn.clicked.connect(self.stop_ngrok)
        self.server_btn.clicked.connect(self.start_running_server)

    def get_positions_from_ib(self):
        positions = self.ib.get_positions()
        for _ in range(100):
            if len(positions) == 0:
                time.sleep(0.1)
            else:
                break
        self.positions = positions
        self.get_positions_btn.setEnabled(True)
        self.get_positions_btn.setText("Get Positions")
        self.display_positions_btn.setEnabled(True)

    def start_running_server(self):
        t = threading.Thread(target=self.run_server)
        t.start()

    def run_server(self):
        subprocess.call('start /wait python RunFlask.py', shell=True)

    def start_running_ngrok(self):

        t = threading.Thread(target=self.run_ngrok)
        t.start()



    def run_ngrok(self):

        subprocess.call('start /wait python RunNgRok.py', shell=True)


    def stop_ngrok(self):
        try:
            from RunNgRok import p

            os.kill(p, signal.SIGTERM)

        except Exception as error:

            print(f'error: {error}')

    def start_getting_positions(self):



        self.table.setRowCount(0)

        self.positions = []

        self.get_positions_btn.setText("Getting")

        self.get_positions_btn.setEnabled(False)

        t = threading.Thread(target=self.get_positions_from_ib)
        t.start()

    def buy_clicked(self):

        try:

            row = self.selected_row

            ticker = self.table.item(row, 0).text()
            asset_type = self.asset_type_dict[self.table.item(row, 1).text()]
            quantity = self.volume.value()

            self.buy(ticker, asset_type, quantity)

            self.table.item(row, 2).setText(str(float(self.table.item(row, 2).text()) + quantity))
        except Exception as error:
            print(f'error: {error}')

    def close_position(self):

        try:

            row = self.selected_row

            ticker = self.table.item(row, 0).text()
            asset_type = self.asset_type_dict[self.table.item(row, 1).text()]
            quantity = float(self.table.item(row, 2).text())

            if quantity > 0:

                self.sell(
                    ticker=ticker,
                    asset_type=asset_type,
                    quantity=quantity
                )
            else:
                self.buy(
                    ticker=ticker,
                    asset_type=asset_type,
                    quantity=abs(quantity)
                )

            self.table.item(row, 2).setText(str(0))
        except Exception as error:
            print(f'error: {error}')

    def sell_clicked(self):

        try:
            row = self.selected_row

            ticker = self.table.item(row, 0).text()
            asset_type = self.asset_type_dict[self.table.item(row, 1).text()]
            quantity = self.volume.value()

            self.sell(ticker, asset_type, quantity)

            self.table.item(row, 2).setText(str(float(self.table.item(row, 2).text()) - quantity))
        except Exception as error:
            print(f'error: {error}')

    def sell(self, ticker, asset_type, quantity):

        try:
            contract = self.ib.make_contract(ticker, asset_type)
            p = self.ib.get_market_data(
                contract=contract,
                data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE],
                live_data=False
            )
            time.sleep(2)

            price = p.close

            self.ib_alternative.sell_ib(
                ticker=ticker,
                asset_type=asset_type,
                quantity=quantity,
                price=price
            )
        except Exception as error:
            print(f'error: {error}')
            traceback.print_exc()
        return

    def buy(self, ticker, asset_type, quantity):

        try:

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

    def fill_table_dict(self, ticker, position_size, asset_type):

        self.table_items[ticker] = {
            'position_size': position_size,
            'asset_type': asset_type,

        }

    def item_clicked(self, it):

        print(it.text())
        print(it.row())

        self.selected_row = it.row()

    def display_positions_clicked(self):

        row_count = self.table.rowCount()

        for p in self.positions:
            position_type = 'LONG' if float(p.position) > 0 else 'SHORT'

            self.table.insertRow(row_count)
            self.table.setItem(row_count, 0, QTableWidgetItem(p.ticker))
            self.table.setItem(row_count, 1, QTableWidgetItem(p.asset_type))
            self.table.setItem(row_count, 2, QTableWidgetItem(str(p.position)))
            self.table.setItem(row_count, 3, QTableWidgetItem(position_type))

            self.fill_table_dict(
                ticker=p.ticker,
                position_size=p.position,
                asset_type=p.asset_type,

            )

            row_count += 1
        self.get_positions_btn.setText("Get Positions")
