from tritki.gui import run_gui

if __name__ == '__main__':
    run_gui()

# import importlib.resources
# import pathlib

# import markdown

# PATH = str((pathlib.Path.cwd() / 'test_data').resolve())


# class Ui(QtWidgets.QMainWindow):
#     def __init__(self):
#         self._current = None
#         super(Ui, self).__init__()
#         with importlib.resources.path('tritki', 'mainwindow.ui') as pth:
#             uic.loadUi(pth, self)
#         self.show()
#         model = QtWidgets.QFileSystemModel(self)
#         model.setRootPath(PATH)
#         self.article_list.setModel(model)
#         self.article_list.setRootIndex(model.index(PATH))
#         self.sel_model = self.article_list.selectionModel()
#         self.sel_model.selectionChanged.connect(self.sel_changed)
#         root = model.index('test_data\\index.md')
#         self.sel_model.select(root, self.sel_model.Select)
#         self.edit_save.clicked.connect(self.do_edit_save)
#         self.edit_bold.clicked.connect(self.do_edit_bold)

#     def do_edit_bold(self):
#         cursor = self.page_edit.textCursor()
#         cursor.setKeepPositionOnInsert(True)
#         data = cursor.selectedText()
#         cursor.insertText(f"**{data}**")
#         self.page_edit.setTextCursor(cursor)
#         self.page_edit.setFocus()

#     def do_edit_save(self):
#         data = self.page_edit.toPlainText()
#         self._current.write_text(data)
#         self.render(self._current)

#     def sel_changed(self, *args):
#         sel = self.sel_model.selection()
#         idxs = sel.indexes()
#         idx = next(iter(idxs))
#         pth = pathlib.Path(self.article_list.model().filePath(idx)).resolve()
#         self._current = pth
#         self.render(pth)

#     def render(self, path):
#         data = path.read_text()
#         html = markdown.markdown(data)
#         self.page_view.setHtml(html)
#         self.page_edit.setPlainText(data)

