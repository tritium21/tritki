import sys

import tritki.exceptions


def run_gui():
    try:
        from PyQt5 import QtWidgets
    except ImportError as e:
        raise tritki.exceptions.UIError("PyQt5 not installed") from e
    from tritki.gui import mainwindow
    app = QtWidgets.QApplication(sys.argv)
    window = mainwindow.MainWindow()
    app.exec_()