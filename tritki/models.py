from contextlib import contextmanager

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
        self._make_session = None
        self.session = None
        self.connect()

    def connect(self):
        configure_mappers()
        self.engine = create_engine(self.uri)
        self._make_session = sessionmaker(self.engine, expire_on_commit=False)
        self.session = self._make_session()
        Base.metadata.create_all(self.engine)
        with self.session_scope() as session:
            import lorem
            for _ in range(5):
                article = Article()
                article.title = lorem.sentence()
                article.content = lorem.text()
                session.add(article)


    @contextmanager
    def session_scope(self):
        try:
            yield self.session
            self.session.commit()
        except:
            self.session.rollback()
            raise
        # finally:
            # session.close()