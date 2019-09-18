from contextlib import contextmanager

from PyQt5.QtCore import QAbstractListModel

from sqlalchemy import Column, Integer, Unicode, UnicodeText, create_engine, DateTime, event
from sqlalchemy.sql import func
from sqlalchemy.orm import configure_mappers, sessionmaker
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy_continuum import make_versioned


make_versioned(user_cls=None)

@as_declarative()
class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, server_onupdate=func.now(), server_default=func.now())

class Article(Base):
    __versioned__ = {}
    title =  Column(Unicode(512))
    content = Column(UnicodeText)

    def __repr__(self):
        content = self.content
        if len(content) >= 50:
            content = f"{content[:47]}..."
        return f"<{self.__class__.__module__}.{self.__class__.__qualname__} - {self.title!r}: {content!r}>"

#TODO: make this thing work so i can update the gui on database update
class ArticleViewModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return super().rowCount(self, parent=parent)

    def data(self, QModelIndex, role=Qt.DisplayRole):
        return super().data(self, QModelIndex, role=role)

    @event.listens_for(Article, 'after_delete')
    def update(self, *args):
        pass

# class Media(Base):
#     __versioned__ = {}
#     path = Column(Unicode(512))
#     storage_path = Column(Unicode(512))

#     def __repr__(self):
#         return f"<{self.__class__.__module__}.{self.__class__.__qualname__}: {self.path!r} -> {self.storage_path!r}>"


class DB:
    def __init__(self, uri='sqlite:///test.db', *, connect=True):
        self.ready = False
        self.uri = uri
        self.engine = None
        self.Session = None
        self.connect()

    def connect(self):
        configure_mappers()
        self.engine = create_engine(self.uri)
        self.Session = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()