from PyQt5 import QtCore, QtWebEngineWidgets, QtWebEngineCore

def make_scheme():
    scheme = QtWebEngineCore.QWebEngineUrlScheme(b'static')
    scheme.setFlags(QtWebEngineCore.QWebEngineUrlScheme.SecureScheme)
    QtWebEngineCore.QWebEngineUrlScheme.registerScheme(scheme)

class StaticHandler(QtWebEngineCore.QWebEngineUrlSchemeHandler):
    def __init__(self, *args, app, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    def requestStarted(self, job):
        url = job.requestUrl()
        path = url.path()
        rep = self.app.static(path)
        if rep is None:
            job.fail(job.UrlNotFound)
            return
        mime = rep[0].encode('ascii')
        buf = QtCore.QBuffer(parent=self)
        buf.open(QtCore.QIODevice.WriteOnly)
        buf.write(rep[1])
        buf.seek(0)
        buf.close()
        job.reply(mime, buf)

class TWebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            self.parent().linkClicked.emit(url)
            return False
        return True

class TWebEngineView(QtWebEngineWidgets.QWebEngineView):
    linkClicked = QtCore.pyqtSignal(QtCore.QUrl)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPage(TWebEnginePage(self))
        self.loadFinished.connect(lambda x: self.history().clear())
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def installStatic(self, app):
        handler = StaticHandler(self, app=app)
        self.page().profile().defaultProfile().installUrlSchemeHandler(b'static', handler)