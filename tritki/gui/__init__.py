import sys

from PyQt5 import QtWidgets

from tritki.gui import mainwindow

def run_gui(app, argv=sys.argv):
    qtapp = QtWidgets.QApplication(argv)
    window = mainwindow.MainWindow(app)
    qtapp.exec_()