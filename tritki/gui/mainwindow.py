try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources  # python 3.6 :(

from PyQt5 import QtWebEngineWidgets, QtWidgets, uic, QtCore, QtGui

_headings = (
    ("Normal", 0),
    ("# Heading 1", 1),
    ("## Heading 2", 2),
    ("### Heading 3", 3),
    ("#### Heading 4", 4),
    ("##### Heading 5", 5),
    ("###### Heading 6", 6),
)

def _default(name):
    def inner():
        print("clicked: ", name)
    return inner


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        self._controller = controller
        with resources.path('tritki.gui', 'mainwindow.ui') as pth:
            uic.loadUi(pth, self)
        self._initialize()
        self.show()

    def _initialize(self):
        for index, (text, data) in enumerate(_headings):
            self.edit_heading.insertItem(
                index,
                text,
                userData=data,
            )
        signals = [
            (self.edit_bold.clicked, "edit_bold_clicked"),
            (self.edit_italic.clicked, "edit_italic_clicked"),
            (self.edit_quote.clicked, "edit_quote_clicked"),
            (self.edit_heading.currentIndexChanged, "edit_heading_currentIndexChanged"),
            (self.edit_link.clicked, "edit_link_clicked"),
            (self.edit_wikilink.clicked, "edit_wikilink_clicked"),
            (self.edit_save.clicked, "edit_save_clicked"),
            (self.search_button.clicked, "search_button_clicked"),
            (self.new_article.clicked, "new_article_clicked"),
        ]
        default_handler = getattr(self._controller, "default", _default("No handler"))
        for signal, name in signals:
            handler = getattr(self._controller, name, default_handler)
            signal.connect(handler)