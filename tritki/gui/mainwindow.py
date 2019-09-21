try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources  # python 3.6 :(

from PyQt5 import QtWebEngineWidgets, QtWidgets, uic, QtCore, QtGui, QtWebEngineCore
from tritki.gui.alchemical import SqlAlchemyTableModel
from tritki.models import Article

stylesheet = """
a.wiki {
    color: #0000ff;
}
a.noexist {
    color: #ff0000;
}
a.external {
    color: #0000aa;
    font-style: italic;
}
"""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app=None):
        self._current_page = None
        super().__init__()
        self.app = app
        with resources.path('tritki.gui', 'mainwindow.ui') as pth:
            uic.loadUi(pth, self)
        self._initialize()
        self.show()
        self.navigate(self.app.mainpage)

    def _initialize(self):
        self.app.register_html(self.set_html)
        self.app.register_plaintext(self.set_plaintext)
        self.app.register_navigate(self.navigate)
        self.article_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._model = model = SqlAlchemyTableModel(
            self.app.db.session,
            Article,
            [("Title", Article.title, "title", {})],
        )
        self.article_list.setModel(model)
        self._selmodel = self.article_list.selectionModel()
        self._selmodel.selectionChanged.connect(self.selection_changed)
        self.edit_save.clicked.connect(self.save)
        self.page_view.anchorClicked.connect(self.link_clicked)
        self.delete_article.clicked.connect(self.do_delete_article)
        document = self.page_view.document()
        document.setDefaultStyleSheet(stylesheet)

    def switch_view(self, view='view'):
        if view == 'edit':
            widget = self.edit_tab
        elif view == 'history':
            widget = self.history_tab
        else:
            widget = self.read_tab
        self.article_viewport.setCurrentWidget(widget)

    def navigate(self, item):
        index = self._model.get_index(item)
        self._selmodel.select(index, self._selmodel.ClearAndSelect)

    def selection_changed(self, new, old):
        idx = next(iter(new.indexes()))
        ()
        item = self._model.data(idx)
        self.app.change_item(item)

    def set_html(self, html):
        self.page_view.setHtml(html)

    def set_plaintext(self, id, plaintext, title):
        self._current_page = id
        self.edit_title.setText(title)
        self.page_edit.setPlainText(plaintext)

    def save(self):
        content = self.page_edit.toPlainText()
        title = self.edit_title.text()
        id = self._current_page
        self.app.save(id, content, title)

    def link_clicked(self, url):
        scheme = url.scheme()
        if scheme not in ('view', 'edit'):
            QtGui.QDesktopServices.openUrl(url)
            return
        target = url.path().lstrip('/')
        if scheme == 'view':
            self.app.navigate(target)
        elif scheme == 'edit':
            self.app.new(target)
            self._model.refresh()
            self.app.navigate(target)
            self.switch_view('edit')

    def do_delete_article(self):
        if not self._selmodel.hasSelection():
            return
        index = self._selmodel.currentIndex()
        item = self._model.get_item(index)
        if item.title == self.app.mainpage:
            return
        mbox = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            f"Delete \"{item.title}\"?",
            f"Are you sure you wish to delete \"{item.title}\"?",
            buttons=QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No
        )
        mbox.setDefaultButton(QtWidgets.QMessageBox.No)
        retval = mbox.exec_()
        if retval == QtWidgets.QMessageBox.Yes:
            self.app.delete(item)
            self._model.refresh()
        else:
            return
        if not self._selmodel.hasSelection():
            print("no current index after delete?")
            return
        newindex = self._selmodel.currentIndex()
        if newindex.row() == index.row():
            self.app.navigate(self.app.mainpage)
            return
        item = self._model.data(newindex)
        self.app.change_item(item)