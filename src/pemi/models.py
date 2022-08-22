from PyQt5 import QtCore, QtGui


class DictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data={}, parent=None):
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

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            self.data[list(self.data.keys())[index.row()]][index.column()] = value
            return True

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def data(self, index: QtCore.QModelIndex, role: int):
        row = index.row()
        col = index.column()
        key = list(self.data.keys())[row]

        if role == QtCore.Qt.BackgroundRole:
            if key in self.highlighted:
                return self.highlighted[key]
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            try:
                return str(self.data[key][col])
            except IndexError:
                return ""


class ListModel(QtGui.QStandardItemModel):
    def __init__(self, data=[]):
        super().__init__()
        for i in data:
            self.appendRow(QtGui.QStandardItem(i))

    def setData(self, data):
        self.clear()
        for i in data:
            self.appendRow(QtGui.QStandardItem(i))
