from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_category_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

class CategoryModel(DeclarativeBase):
    """Sqlalchemy categorys model"""
    __tablename__ = "categorytable"

    ID_category = Column(Integer, primary_key=True)
    name = Column('name', String)
    description = Column('description', String, nullable=True)
    url = Column('url', String, nullable=True)
    ID_site = Column('ID_site', String, nullable=True)
    hash = Column('hash', String, nullable=True)

class ProductModel(DeclarativeBase):
    """SQLAlchemy product model"""
    __tablename__= "productable"

    ID_product = Column(Integer, primary_key=True)
    name = Column('name', String, nullable=True)
    ID_site = Column('ID_site', String, nullable=True)
    url = Column('url', String, nullable=True)
    ID_desc = Column('ID_desc', String, nullable=True)
    date_in = Column('date_in', String, nullable=True)
    date_mod = Column('date_mod', String, nullable=True)
    price = Column('price', String, nullable=True)
    currency = Column('currency', String, nullable=True)
    available = Column('available', String, nullable=True)
    category = Column('category', String, nullable=True)
    hash = Column('hash', String, nullable=True)
