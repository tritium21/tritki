from contextlib import contextmanager

from whooshalchemy import IndexService
from sqlalchemy import Column, Integer, UnicodeText, create_engine, DateTime, event
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlalchemy.sql import func
from sqlalchemy.orm import configure_mappers, sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
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
    def __init__(self, *, app, database_uri='sqlite:///test.db', index_path='.', **args):
        self.app = app
        self.database_uri = database_uri
        self.index_path = index_path
        configure_mappers()
        self.engine = create_engine(self.database_uri)
        self.Session = sessionmaker(self.engine, autoflush=True, expire_on_commit=True)
        self.session = self.Session()
        Base.metadata.create_all(self.engine)
        self.index = IndexService(whoosh_base=self.index_path, session=self.session)
        self.index.register_class(Article)

    def list_articles(self):
        with self.session_scope() as session:
            return session.query(Article).all()
    
    def delete_article(self, article):
        with self.session_scope() as session:
            session.delete(article)
        self.app.updated()

    def save(self, id, content, title):
        with self.session_scope() as session:
            article = session.query(Article).filter(Article.id == id).first()
            article.content = content
            if article.title != self.app.mainpage:
                article.title = title
        self.app.updated()
        return article
    
    def new(self, title):
        with self.session_scope() as session:
            article = Article()
            article.title = title
            article.content = "Write some content"
            session.add(article)
        self.app.updated()
        return article

    def exists(self, title):
        with self.session_scope() as session:
            return session.query(Article).filter(Article.title == title).scalar() is not None

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except (SQLAlchemyError, DBAPIError) as e:
            session.rollback()
            raise
        finally:
            pass
            #session.close()
