# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from models import CategoryModel, db_connect, create_category_table, ProductModel
from items import CategoryItem, ProductItem
from sqlalchemy import text

class farmator(object):
    """FarmaciaFrias pipeline for storing scraped items in the database"""
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates categorytable table.
        """
        engine = db_connect()
        create_category_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save categorys in the database.

        This method is called for every item pipeline component.

        """
        session = self.Session()
        itemModel = False

        # Comprueba el tipo de item a insertar
        if type(item) == type(CategoryItem()):
            if self.hashexist(session, item):
                self.printaction('La categoria ya existe', item)
                session.close()
                return
            else: 
                itemModel = CategoryModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo el registro', item)

        elif type(item) == type(ProductItem()):
            # Si ya existe no lo inserta
            if self.hashexist(session, item):
                self.printaction('El producto ya existe', item)
                session.close()

            # Si existe pero ha cambiado lo actualiza
            elif type(item) == type(ProductItem()) and self.urlexist(session, item['url']):
                self.updateitem(session, item)
                self.conection_add_commit(session, False, item)
                self.printaction('Se modifico el registro', item)
            else:
                itemModel = ProductModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo nuevo producto', item)

    def conection_add_commit(self, session, itemModel, item): 
        try:
            if itemModel:
                session.add(itemModel)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        if itemModel and item:
            return item

    def hashexist(self, session, item):
        # Comprueba si existe un hash
        # incluir modo factoria

        if type(item) == type(CategoryItem()):
            hashlist = session.execute(
                text("SELECT * FROM categorytable WHERE hash=:hashtocheck"),
                {"hashtocheck": item['hash']}
                )
        elif type(item) == type(ProductItem()):
            hashlist = session.execute(
                text("SELECT * FROM productable WHERE hash=:hashtocheck"),
                {"hashtocheck": item['hash']}
                )
        if hashlist.rowcount != 0:
            return True
        else:
            return False

    def urlexist(self, session, urltocheck):
        #Comprueba si existe la url de un producto en la base de datos
        #Falta añadir caso de que URL no sea buena
        urllist = session.execute(
            text("SELECT * FROM productable WHERE url=:urlcheck"),
            {"urlcheck": urltocheck}
            )
        if urllist.rowcount != 0:
            return True
        else:
            return False
    def printaction(self, actionstring, item):
        print('<--  PIPELINE DEBUG  --> ', actionstring)
        if item:       
            print('HASH: ', item['hash'])
            print('name: ', item['name'])

    def updateitem(self, session, item):
        #Actualiza un item existente
        if type(item) == type(CategoryItem()):
            print('Building update Category')

        elif type(item) == type(ProductItem()):
            updateobj = session.execute(
                text("UPDATE  productable SET name=:newname, price=:newprice, currency=:newcurrency, available=:newavailable, hash=:newhash WHERE url=:url"),
                {"newname": item['name'], "newprice": item['price'], "newcurrency": item['currency'], "newavailable": item['available'], "newhash": item['hash'], "url": item['url']}
            )
            session.commit()


