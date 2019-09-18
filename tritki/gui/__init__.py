import sys

from PyQt5 import QtWidgets

from tritki.gui import mainwindow

def run_gui(argv=sys.argv):
    app = QtWidgets.QApplication(argv)
    window = mainwindow.MainWindow()
    app.exec_()