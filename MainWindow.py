from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QPushButton
from PyQt6.uic import loadUi
from IBInterface import MainIB
import random
import time
class MainWindow(QMainWindow):

    def __init__(self):

        super(MainWindow, self).__init__()
        loadUi('MainWindow.ui', self)
        self.ib = MainIB(client_id=random.randint(20, 30))

        self.get_positions_btn.clicked.connect(self.get_positions_clicked)


    def get_positions_clicked(self):

        positions = self.ib.get_positions()
        time.sleep(2)


        row_count = self.table.rowCount()

        for p in positions:
            position_type = 'LONG' if float(p.position) > 0 else 'SHORT'
            self.table.setItem(row_count, 0, QTableWidgetItem(p.ticker))
            self.table.setItem(row_count, 1, QTableWidgetItem(p.position))
            self.table.setItem(row_count, 2, QTableWidgetItem(position_type))
            row_count += 1












