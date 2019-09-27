from contextlib import contextmanager

from whooshalchemy import IndexService
from sqlalchemy import Column, Integer, UnicodeText, create_engine, DateTime, event
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlalchemy.sql import func
from sqlalchemy.orm import configure_mappers, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_continuum import make_versioned


make_versioned(user_cls=None)

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    __versioned__ = {}
    __searchable__ = ['title', 'content']
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, server_onupdate=func.now(), server_default=func.now())
    title =  Column(UnicodeText(512))
    content = Column(UnicodeText)

    def __repr__(self):
        content = self.content
        if len(content) >= 25:
            content = f"{content[:22]}..."
        return f"<{self.__class__.__module__}.{self.__class__.__qualname__} - {self.title!r}: {content!r}>"

class DB:
    def __init__(self, database_uri='sqlite:///test.db', index_path='.', **args):
        self.database_uri = database_uri
        self.index_path = index_path
        configure_mappers()
        self.engine = create_engine(self.database_uri)
        self._make_session = sessionmaker(self.engine, autoflush=True, expire_on_commit=True)
        self.session = self._make_session()
        Base.metadata.create_all(self.engine)
        self.index = IndexService(whoosh_base=self.index_path, session=self.session)
        self.index.register_class(Article)

    @contextmanager
    def session_scope(self):
        try:
            yield self.session
            self.session.commit()
        except (SQLAlchemyError, DBAPIError) as e:
            self.session.rollback()
            raise
