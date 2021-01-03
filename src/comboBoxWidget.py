from PyQt5.QtWidgets import QComboBox


class ComboBoxWidget(QComboBox):

    def __init__(self, filepath, parent=None):
        QComboBox.__init__(self, parent)
        self.filepath = filepath

        self.items = self.get_list()
        self.add_items()

    def get_list(self):
        items = []
        with open(self.filepath, 'r') as file:
            for line in file:
                items.append(line.strip('\n'))
        return items

    def add_items(self):
        self.addItems(self.items)
