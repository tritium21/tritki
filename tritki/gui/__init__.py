import sys

import qdarkstyle
from PyQt5 import QtWebEngineWidgets, QtWidgets

from tritki.gui import mainwindow, webview

qtapp = None

def run_gui(app, argv=sys.argv):
    webview.make_scheme()
    global qtapp
    qtapp = QtWidgets.QApplication(argv)
    window = mainwindow.MainWindow(app)
    qtapp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    qtapp.exec_()