from PyQt5 import QtCore, QtGui


class DictTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data={}, parent=None, editable=False, row_count=64):
        super().__init__(parent)
        self._data = data
        self._headers = list(data.keys())
        self.editable = editable
        self.row_count = row_count

        self.highlighted = {}

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int):
        if role == QtCore.Qt.DisplayRole:
            try:
                return self._headers[section]
            except IndexError:
                return ""

    def columnCount(self, parent=None):
        return self.row_count

    def rowCount(self, parent=None):
        return len(list(self._data.keys()))

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            self._data[list(self._data.keys())[index.row()]][index.column()] = value
            return True
        elif role == QtCore.Qt.ItemDataRole:
            self._data[index] = value
            row = list(self._data.keys()).index(index)
            self.headerDataChanged.emit(QtCore.Qt.Orientation.Vertical, row, row)
            self.dataChanged.emit(self.index(row, 0), self.index(row, len(value) - 1))
            return True

    def getData(self) -> dict:
        return self._data

    def insertRow(self, row, index=None, key=""):
        if index is None:
            index = self.index(0, 0)
        self.beginInsertRows(index, row, row + 1)
        self._data[key] = ["Unknown"]
        self._headers = list(self._data.keys())
        self.endInsertRows()

    def flags(self, index):
        if self.editable:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
        else:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def data(self, index: QtCore.QModelIndex, role: int):
        row = index.row()
        col = index.column()
        key = list(self._data.keys())[row]

        if role == QtCore.Qt.BackgroundRole:
            if key in self.highlighted:
                return self.highlighted[key]
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            try:
                return str(self._data[key][col])
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
