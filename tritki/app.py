import os
import pathlib

import jinja2

import tritki.models
from tritki.models import Article
import tritki.gui
import tritki.markdown

DATABASE_NAME = 'tritki.db'
INDEX_NAME = 'index'

class App:
    def __init__(self, *, data_path=None, create=False, qt_args=None):
        self.mainpage = 'Main Page'
        self.jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader('tritki', 'templates'),
            autoescape=jinja2.select_autoescape(
                enabled_extensions=[],
                disabled_extensions=['html'],
                default_for_string=False,
                default=False,
            ),
        )
        self.markdown = tritki.markdown.Converter(self)
        self.data_path = None
        self.database_uri = None
        self.db = None
        self._html_callbacks = []
        self._plaintext_callbacks = []
        self._navigate_callbacks = []
        if data_path is not None:
            self.load(data_path, create=create)
        tritki.gui.run_gui(self, qt_args)

    def load(self, data_path, *, create=False):
        data_path = pathlib.Path(data_path).resolve(strict=not create)
        index_path = (data_path / INDEX_NAME).resolve(strict=not create)
        if create:
            data_path.mkdir(parents=True)
            index_path.mkdir(parents=True)
        db_path = (data_path / DATABASE_NAME).resolve(strict=not create)
        self.database_uri = db_path.as_uri().replace('file:', 'sqlite:')
        self.db = tritki.models.DB(uri=self.database_uri, indexdir=index_path)
        if create:
            self.new(self.mainpage)
        self.data_path = data_path

    def register_html(self, callable_):
        if callable(callable_):
            self._html_callbacks.append(callable_)

    def register_plaintext(self, callable_):
        if callable(callable_):
            self._plaintext_callbacks.append(callable_)
    
    def register_navigate(self, callable_):
        if callable(callable_):
            self._navigate_callbacks.append(callable_)

    def navigate(self, item):
        for callable_ in self._navigate_callbacks:
            callable_(item)

    def change_item(self, item):
        with self.db.session_scope() as session:
            article = session.query(Article).filter(Article.title == item).first()
            self.update_page(article)

    def update_page(self, article):
        html = self.render(article)
        for callable_ in self._html_callbacks:
            callable_(html)
        for callable_ in self._plaintext_callbacks:
            callable_(article.id, article.content, article.title)        

    def save(self, id, content, title):
        with self.db.session_scope() as session:
            article = session.query(Article).filter(Article.id == id).first()
            article.content = content
            if article.title != self.mainpage:
                article.title = title
        self.update_page(article)
    
    def new(self, title):
        with self.db.session_scope() as session:
            article = Article()
            article.title = title
            article.content = "Write some content"
            session.add(article)

    def exists(self, name):
        with self.db.session_scope() as session:
            return session.query(Article).filter(Article.title == name).scalar() is not None

    def render(self, article):
        converted = self.markdown.convert(article.content)
        template = self.jinja_env.get_template('article.html')
        rendered = template.render(title=article.title, content=converted)
        return rendered

    def delete(self, article):
        with self.db.session_scope() as session:
            session.delete(article)