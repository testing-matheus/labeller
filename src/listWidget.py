from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import pyqtSlot


class ListWidget(QListWidget):

    def __init__(self, filepath, parent=None):
        QListWidget.__init__(self, parent)
        self.filepath = filepath

        self.items = self.get_list()
        self.add_items()
        self.setCurrentRow(0)

    def get_list(self):
        items = []
        with open(self.filepath, 'r') as file:
            for line in file:
                items.append(line.strip('\n'))
        return items

    def add_items(self):
        self.addItems(self.items)

    def get_items(self):
        return self.items

    def set_row(self, index):
        if index < len(self.items):
            self.setCurrentRow(index)

    @pyqtSlot()
    def set_row_1(self):
        self.set_row(0)

    @pyqtSlot()
    def set_row_2(self):
        self.set_row(1)

    @pyqtSlot()
    def set_row_3(self):
        self.set_row(2)

    @pyqtSlot()
    def set_row_4(self):
        self.set_row(3)

    @pyqtSlot()
    def set_row_5(self):
        self.set_row(4)

    @pyqtSlot()
    def set_row_6(self):
        self.set_row(5)

    @pyqtSlot()
    def set_row_7(self):
        self.set_row(6)

    @pyqtSlot()
    def set_row_8(self):
        self.set_row(7)

    @pyqtSlot()
    def set_row_9(self):
        self.set_row(8)
