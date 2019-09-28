from importlib import resources

from functools import partial

from PyQt5 import QtWidgets, uic, QtCore, QtGui
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
        self.article_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._model = model = SqlAlchemyTableModel(
            self.app.db.session,  # Need to fix this - too coupled
            Article,  # and this.
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
        self.page_edit.textCursor().setKeepPositionOnInsert(True)
        self.page_edit.spelling_provider = self.app.spelling_provider
        self.edit_bold.clicked.connect(partial(self.inline_format, '**'))
        self.edit_italic.clicked.connect(partial(self.inline_format, '*'))
        self.edit_wikilink.clicked.connect(self.insert_wikilink)
        self.edit_link.clicked.connect(self.insert_link)
        self.new_article.clicked.connect(self.do_new_article)
        self.search_button.clicked.connect(self.search_articles)
        self.search_text.returnPressed.connect(self.search_button.click)

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


    # Editor methods
    def inline_format(self, format):
        cursor = self.page_edit.textCursor()
        data = cursor.selectedText()
        cursor.insertText(f"{format}{data}{format}")
        self.page_edit.setFocus()

    def insert_link(self):
        cursor = self.page_edit.textCursor()
        name = cursor.selectedText()
        ref = None
        if not name.strip():
            name, status = QtWidgets.QInputDialog.getText(
                self,
                "Name for link",
                "Name",
                text=ref
            )
            if not status:
                return
        ref, status = QtWidgets.QInputDialog.getText(
            self,
            "Target for link",
            "Target",
            text="https://"
        )
        if not status:
            return
        cursor.insertText(f"[{name}]({ref})")
        self.page_edit.setFocus()

    def insert_wikilink(self):
        cursor = self.page_edit.textCursor()
        ref = cursor.selectedText()
        name = None
        if not ref.strip():
            items = [i.title for i in self._model.results]
            ref, status = QtWidgets.QInputDialog.getItem(
                self,
                "Select an article",
                "Article",
                items,
                0,
                True,
            )
            if not status:
                return
            name, status = QtWidgets.QInputDialog.getText(
                self,
                "Name for link",
                "Name",
                text=ref
            )
            if not status:
                return
            if ref == name:
                name = None
        data = '|'.join(x for x in [ref, name] if x)
        cursor.insertText(f"[[{data}]]")
        self.page_edit.setFocus()
        
    def save(self):
        content = self.page_edit.toPlainText()
        title = self.edit_title.text()
        id = self._current_page
        self.app.save(id, content, title)

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
        self.edit_title.setText(title)
        self.page_edit.setPlainText(plaintext)

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

