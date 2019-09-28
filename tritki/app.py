import os
import pathlib
import sys

import appdirs
import jinja2
import toml

import tritki.models
from tritki.models import Article
import tritki.gui
import tritki.markdown
import tritki.spelling

DATABASE_NAME = 'tritki.db'
INDEX_NAME = 'index'


class GlobalState:
    def __init__(self):
        self.appdirs = appdirs.AppDirs('tritki')
        self.state_file = pathlib.Path(self.appdirs.user_config_dir) / 'state.toml'

    def get_state(self):
        if not self.state_file.exists():
            return {}
        return toml.loads(self.state_file.read_text(encoding="UTF-8"))

    def set_state(self, obj):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(toml.dumps(obj), encoding="UTF-8")


if getattr(sys, 'frozen', False):
    pth = str(pathlib.Path(sys._MEIPASS).resolve(strict=True) / 'data' / 'templates')
    LOADER = jinja2.FileSystemLoader(pth)
else:
    LOADER = jinja2.PackageLoader('tritki.data', 'templates')

class App:
    def __init__(self, *, data_path=None, create=False, qt_args=None):
        self.global_state = GlobalState()
        self.mainpage = 'Main Page'
        self.jinja_env = jinja2.Environment(
            loader=LOADER,
            autoescape=jinja2.select_autoescape(
                enabled_extensions=[],
                disabled_extensions=['html'],
                default_for_string=False,
                default=False,
            ),
        )
        self.markdown = tritki.markdown.Converter(self)
        self.spelling_provider = tritki.spelling.Spelling()
        if data_path is None:
            data_path = self.global_state.get_state().get('data_path')
        self.data_path = pathlib.Path(data_path).resolve(strict=not create)
        self.global_state.set_state({'data_path': data_path})
        self.config_path = (self.data_path / 'config.toml').resolve(strict=not create)
        self.config = {
            'database_uri': (self.data_path / DATABASE_NAME).resolve(strict=not create).as_uri().replace('file:', 'sqlite:'),
            'index_path': str((self.data_path / INDEX_NAME).resolve(strict=not create)),
            'last_page': self.mainpage,
        }
        if create:
            self.config['index_path'].mkdir(parents=True)
            self.write_config()
        else:
            self.config.update(self.read_config())
        self.db = tritki.models.DB(**self.config)
        if create:
            self.new(self.mainpage)
        self._html_callbacks = []
        self._plaintext_callbacks = []
        self._navigate_callbacks = []
        tritki.gui.run_gui(self, qt_args)

    def search(self, term):
        query = Article.search_query(term)
        return [x.title for x in query]

    def write_config(self):
        self.config_path.write_text(toml.dumps(self.config), encoding="UTF-8")

    def read_config(self):
        return toml.loads(self.config_path.read_text(encoding="UTF-8"))

    def last_page(self, item):
        self.config['last_page'] = item
        self.write_config()

    def register_html(self, callable_):
        if callable(callable_):
            self._html_callbacks.append(callable_)

    def register_plaintext(self, callable_):
        if callable(callable_):
            self._plaintext_callbacks.append(callable_)
    
    def register_navigate(self, callable_):
        if callable(callable_):
            self._navigate_callbacks.append(callable_)

    def navigate(self, item=None):
        if item is None:
            item = self.config['last_page']
        for callable_ in self._navigate_callbacks:
            callable_(item)

    def change_item(self, item):
        with self.db.session_scope() as session:
            article = session.query(Article).filter(Article.title == item).first()
            self.update_page(article)

    def update_page(self, article):
        self.last_page(article.title)
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