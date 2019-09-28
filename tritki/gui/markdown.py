from importlib import resources
from functools import partial

from PyQt5 import QtWidgets, uic, QtCore, QtGui

class MarkdownEditor(QtWidgets.QWidget):
    save = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        with resources.path('tritki.data', 'markdown_editor.ui') as pth:
            uic.loadUi(pth, self)
        self.page_edit.textCursor().setKeepPositionOnInsert(True)
        
        self.edit_bold.clicked.connect(partial(self.do_inline_format, '**'))
        self.edit_italic.clicked.connect(partial(self.do_inline_format, '*'))
        self.edit_wikilink.clicked.connect(self.do_insert_wikilink)
        self.edit_link.clicked.connect(self.do_insert_link)
        self.edit_save.clicked.connect(self.do_save)

    @property
    def spelling_provider(self):
        return self.page_edit.spelling_provider

    @spelling_provider.setter
    def spelling_provider(self, item):
        self.page_edit.spelling_provider = item

    def setPlainText(self, plaintext):
        self.page_edit.setPlainText(plaintext)

    def setTitle(self, title):
        self.edit_title.setText(title)

    # Editor methods
    def do_inline_format(self, format):
        cursor = self.page_edit.textCursor()
        data = cursor.selectedText()
        cursor.insertText(f"{format}{data}{format}")
        self.page_edit.setFocus()

    def do_insert_link(self):
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

    def do_insert_wikilink(self):
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
        
    def do_save(self):
        title = self.edit_title.text()
        content = self.page_edit.toPlainText()
        self.save.emit(content, title)