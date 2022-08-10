from PyQt5 import QtCore


class DictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data=[[]], parent=None):
        super().__init__(parent)
        self.data = data

        self.highlighted = {}

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return "Column " + str(section)
            else:
                return "Row " + str(section)

    def columnCount(self, parent=None):
        return len(self.data[list(self.data.keys())[0]]) + 1

    def rowCount(self, parent=None):
        return len(list(self.data.keys()))

    def data(self, index: QtCore.QModelIndex, role: int):
        row = index.row()
        col = index.column()
        key = list(self.data.keys())[row]

        if role == QtCore.Qt.BackgroundRole:
            try:
                return self.data[key]
            except KeyError:
                return
        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return key
            else:
                return str(self.data[key][col - 1])
