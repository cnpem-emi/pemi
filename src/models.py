from PyQt5 import QtCore


class DictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data=[[]], parent=None):
        super().__init__(parent)
        self.data = data
        self._headers = list(data.keys())

        self.highlighted = {}

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            try:
                return self._headers[section]
            except IndexError:
                return ""

    def columnCount(self, parent=None):
        return 64  # Largest list returned by UDC

    def rowCount(self, parent=None):
        return len(list(self.data.keys()))

    def data(self, index: QtCore.QModelIndex, role: int):
        row = index.row()
        col = index.column()
        key = list(self.data.keys())[row]

        if role == QtCore.Qt.BackgroundRole:
            if key in self.highlighted:
                return self.highlighted[key]
        if role == QtCore.Qt.DisplayRole:
            try:
                return str(self.data[key][col])
            except IndexError:
                return ""
