from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QPushButton
from PyQt6.uic import loadUi
from IBInterface import MainIB
import random
import time
import threading
class MainWindow(QMainWindow):

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi('MainWindow.ui', self)
        self.ib = MainIB(client_id=random.randint(20, 30))

        self.display_positions_btn.clicked.connect(self.display_positions_clicked)
        self.get_positions_btn.clicked.connect(self.start_getting_positions)

        self.positions = None


    def get_positions_from_ib(self):

        positions = self.ib.get_positions()

        for _ in range(10):

            if len(positions) == 0:
                time.sleep(0.01)
            else:
                break
        self.positions = positions
        self.get_positions_btn.setEnabled(True)
        self.get_positions_btn.setText("Done")

    def start_getting_positions(self):

        self.positions = []

        self.get_positions_btn.setText("Getting")

        self.get_positions_btn.setEnabled(False)

        t = threading.Thread(target=self.get_positions_from_ib)
        t.start()



    def display_positions_clicked(self):



        positions = self.ib.get_positions()



        row_count = self.table.rowCount()

        for p in positions:
            position_type = 'LONG' if float(p.position) > 0 else 'SHORT'
            self.table.setItem(row_count, 0, QTableWidgetItem(p.ticker))
            self.table.setItem(row_count, 1, QTableWidgetItem(p.position))
            self.table.setItem(row_count, 2, QTableWidgetItem(position_type))
            row_count += 1












