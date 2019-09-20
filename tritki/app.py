import os
import pathlib

import tritki.models
from tritki.models import Article
import tritki.gui
import tritki.render

DATABASE_NAME = 'tritki.db'

class App:
    def __init__(self, *, data_path=None, create=False, qt_args=None):
        self.data_path = None
        self.database_uri = None
        self.db = None
        self._html_callbacks = []
        self._plaintext_callbacks = []
        if data_path is not None:
            self.load(data_path, create=create)
        tritki.gui.run_gui(self, qt_args)

    def load(self, data_path, *, create=False):
        data_path = pathlib.Path(data_path).resolve(strict=not create)
        if create:
            data_path.mkdir(parents=True)
        db_path = (data_path / DATABASE_NAME).resolve(strict=not create)
        self.database_uri = db_path.as_uri().replace('file:', 'sqlite:')
        self.db = tritki.models.DB(uri=self.database_uri)
        self.data_path = data_path

    def register_html(self, callable_):
        if callable(callable_):
            self._html_callbacks.append(callable_)

    def register_plaintext(self, callable_):
        if callable(callable_):
            self._plaintext_callbacks.append(callable_)
    
    def change_item(self, item):
        with self.db.session_scope() as session:
            article = session.query(Article).filter(Article.title == item).first()
            html = tritki.render.render(article)
            for callable_ in self._html_callbacks:
                callable_(html)
            for callable_ in self._plaintext_callbacks:
                callable_(article.content, article.title)