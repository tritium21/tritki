from sqlalchemy import Column, Integer, Unicode, UnicodeText, create_engine
from sqlalchemy.orm import configure_mappers
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_continuum import make_versioned

make_versioned(user_cls=None)
Base = declarative_base()

class Article(Base):
    __versioned__ = {}
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    name =  Column(Unicode(512))
    content = Column(UnicodeText)


if __name__ == '__main__':
    configure_mappers()
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)