from sqlalchemy import create_engine, Column, Integer, String 
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

import settings

DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**settings.DATABASE))

def create_all_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

class CategoryModel(DeclarativeBase):
    """Sqlalchemy categorys model"""
    __tablename__ = "categorytable"

    id = Column(Integer, primary_key=True)
    id_site = Column(Integer, ForeignKey('sitetable.id'))
    name = Column('name', String, nullable=True)
    description = Column('description', String, nullable=True)
    short_desc = Column('short_desc', String, nullable=True)
    parent = Column('parent', String, nullable=True)
    url = Column('url', String, nullable=True)
    hash = Column('hash', String, nullable=True)
    updated = Column('updated', String, nullable=True)

    site = relationship("SiteModel", backref=backref('categories', order_by=id))


class ProductModel(DeclarativeBase):
    """SQLAlchemy product model
        Crea la tabla productable
        Relacion con sitetable campo id_site
        Relacion con imgtable campo url
        Relacion con desc"""
    __tablename__= "productable"

    id = Column(Integer, primary_key=True)
    id_category = Column(Integer, ForeignKey('categorytable.id'))
    name = Column('name', String, nullable=True)
    id_site = Column('id_site', Integer, nullable=False)
    url = Column('url', String, nullable=True)
    id_desc = Column('id_desc', String, nullable=True)
    date_in = Column('date_in', String, nullable=True)
    date_mod = Column('date_mod', String, nullable=True)
    price = Column('price', String, nullable=True)
    currency = Column('currency', String, nullable=True)
    available = Column('available', String, nullable=True)
    categoryname = Column('categoryname', String, nullable=True)
    subcategory = Column('subcat', String, nullable=True)
    cn = Column('cn', String, nullable=True)
    hash = Column('hash', String, nullable=True)

    category = relationship("CategoryModel", backref=backref('products', order_by=id))

class SiteModel(DeclarativeBase):
    """ SQLAlchemy SiteModel
        Crea la tabla sitetable
        Relacion con todas las demas campo id_site"""
    __tablename__ = "sitetable"

    id = Column(Integer, primary_key=True)
    name = Column('name', String, nullable=True)
    url = Column('rootpath', String, nullable=True)
    date_in = Column('date_in', String, nullable=True)
    sp1_name = Column('sp1_name', String, nullable=True)
    sp1_status = Column('sp1_status', String, nullable=True)
    sp2_name = Column('sp2_name', String, nullable=True)
    sp2_status = Column('sp2_status', String, nullable=True)
    check_spname = Column('check_spname', String, nullable=True)
    last_update = Column('last_update', String, nullable=True)
    error_log = Column('error_log', String, nullable=True)
    cp = Column('cp', String, nullable=True)
    ciudad = Column('ciudad', String, nullable=True)
    provincia = Column('provincia', String, nullable=True)
    pais = Column('pais', String, nullable=True)
    guardias = Column('guardias', String, nullable=True)
    tlf = Column('tlf',String, nullable=True)
    fax = Column('fax', String, nullable=True)
    movil = Column('movil', String, nullable=True)
    street = Column('street', String, nullable=True)
    hash = Column('hash', String, nullable=True)


class ImgModel(DeclarativeBase):
    """Sqlalchemy ImgModel model
       Crea la tabla imgtable
       Relacion con sitetable campo id_site
       Relacion con productable campo producturl"""
    __tablename__ = "imgtable"

    id = Column(Integer, primary_key=True)
    id_product = Column(Integer, ForeignKey('productable.id'))
    id_site = Column(Integer, ForeignKey('sitetable.id'))
    producturl = Column('producturl', String, nullable=True)
    size = Column('size', String, nullable=True)
    source_url = Column('source_url', String, nullable=True)
    internal_url = Column('internal_url', String, nullable=True)
    img_type = Column('img_type', String, nullable=True)
    hash = Column('hash', String, nullable=True)

    product = relationship("ProductModel", backref=backref('images', order_by=id))

class DescriptionModel(DeclarativeBase):
    """Sqlalchemy  model
       Crea la tabla desctable
        Relacion con sitetable capo id_site
        Relacion con productable campo producturl
        Relacionado con imgtable campo producturl"""
    __tablename__ = "desctable"

    id = Column(Integer, primary_key=True)
    id_product = Column(Integer, ForeignKey('productable.id'))
    #id_site = Column('id_site', Integer, nullable=True)#quitar? desde id_product
    id_site = Column(Integer, ForeignKey('sitetable.id'))
    titulo = Column('titulo', String, nullable=True)
    subtitulo = Column('subtitulo', String, nullable=True)
    texto = Column('texto', String, nullable=True)
    producturl = Column('producturl', String, nullable=True)
    desc_date = Column('desc_date', String, nullable=True)
    desc_type = Column('desc_type', String, nullable=True)
    hash = Column('hash', String, nullable=False)

    product = relationship("ProductModel", backref=backref('descriptions', order_by=id))
