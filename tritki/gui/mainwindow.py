from importlib import resources

from tritki.gui.alchemical import SqlAlchemyTableModel
from tritki.models import Article

from PyQt5 import QtWidgets, uic, QtCore, QtGui


class MListWidget(QtWidgets.QListWidget):
    enterPressed = QtCore.pyqtSignal(QtWidgets.QListWidgetItem)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.enterPressed.emit(self.currentItem())
        return super().keyPressEvent(event)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app=None):
        self._current_page = None
        super().__init__()
        self.app = app
        with resources.path('tritki.data', 'mainwindow.ui') as pth:
            uic.loadUi(pth, self)
        self._initialize()
        self.show()
        self.app.navigate()

    def _initialize(self):
        # <temporary!>
        self.article_viewport.setTabEnabled(
            2,
            False,
        )
        # </temporary!>
        self.app.register_html(self.set_html)
        self.app.register_plaintext(self.set_plaintext)
        self.app.register_navigate(self.navigate)
        self.edit_tab.spelling_provider = self.app.spelling_provider
        self.article_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._model = model = SqlAlchemyTableModel(
            self.app.db.session,  # Need to fix this - too coupled
            Article,  # and this.
            [("Title", Article.title, "title", {})],
        )
        self.article_list.setModel(model)
        self._selmodel = self.article_list.selectionModel()
        self._selmodel.selectionChanged.connect(self.selection_changed)
        self.page_view.linkClicked.connect(self.link_clicked)
        self.page_view.installStatic(self.app)
        self.delete_article.clicked.connect(self.do_delete_article)
        self.new_article.clicked.connect(self.do_new_article)
        self.search_button.clicked.connect(self.search_articles)
        self.search_text.returnPressed.connect(self.search_button.click)
        self.edit_tab.save.connect(self.save)

    def save(self, content, title):
        self.app.save(self._current_page, content, title)

    # Article list methods
    def search_articles(self):
        search_text = self.search_text
        search_button = self.search_button
        article_list = self.article_list
        al_layout = self.article_list_layout
        s_layout = self.search_layout

        search_list = MListWidget(self)
        clear_button = QtWidgets.QPushButton("Clear Search", self)

        def reset():
            al_layout.replaceWidget(search_list, article_list)
            s_layout.replaceWidget(clear_button, search_button)
            search_list.deleteLater()
            clear_button.deleteLater()
            article_list.show()
            search_button.show()

        def item_clicked(item):
            self.switch_view()
            self.app.navigate(item.text())
            reset()

        clear_button.clicked.connect(reset)
        search_list.itemDoubleClicked.connect(item_clicked)
        search_list.enterPressed.connect(item_clicked)
        search_list.setStyleSheet("MListWidget {background-color: Gainsboro};");

        # this is where search sits!
        text = search_text.text()
        items = self.app.search(text)
        if not len(items):
            pos = self.mapToGlobal(search_text.pos())
            QtWidgets.QToolTip.showText(pos, "No results")
            search_list.deleteLater()
            clear_button.deleteLater()
            return
        search_list.addItems(items)
        search_list.item(0).setSelected(True)
        # that was where search sits

        al_layout.replaceWidget(article_list, search_list)
        s_layout.replaceWidget(search_button, clear_button)
        search_list.setFocus()
        article_list.hide()
        search_button.hide()

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

    def do_new_article(self):
        target, status = QtWidgets.QInputDialog.getText(
            self,
            "New article name...",
            "Name",
        )
        if not status:
            return
        self.app.new(target)
        self._model.refresh()
        self.app.navigate(target)
        self.switch_view('edit')


    # Navigation methods - major refactor needed.
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
        item = self._model.data(idx)
        self.app.change_item(item)
        self.switch_view()

    def set_html(self, html):
        self.page_view.setHtml(html)

    def set_plaintext(self, id, plaintext, title):
        self._current_page = id
        self.edit_tab.setTitle(title)
        self.edit_tab.setPlainText(plaintext)

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

