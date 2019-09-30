from PyQt5 import QtCore

class ArticleListModel(QtCore.QAbstractListModel):
    def __init__(self, *args, app, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.app.register_updated(self.refresh)
        self._data = []
        self._map = {}
        self.refresh()

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant('Article')
        return QtCore.QVariant()

    def refresh(self):
        self.layoutAboutToBeChanged.emit()
        self._data = self.app.list_articles()
        self._map = {e.title: self.createIndex(i, 0) for i, e in enumerate(self._data)}
        self.layoutChanged.emit()

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def rowCount(self, parent):
        return len(self._data)
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.UserRole:
            return self._data[index.row()]
        elif role == QtCore.Qt.DisplayRole:
            return self._data[index.row()].title
        else:
            return QtCore.QVariant()

    def map(self, title):
        return self._map.get(title)