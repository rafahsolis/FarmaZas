# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from models import CategoryModel, db_connect, create_category_table, ProductModel
from items import CategoryItem, ProductItem
from sqlalchemy import text

class FarmaciaFriasPipeline(object):
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

        if type(item) == type(CategoryItem()):
            itemModel = CategoryModel(**item)

        elif type(item) == type(ProductItem()):
            if self.hashexist(session, item['hash']):
                exit()
            elif self.urlexist(session, item['url']):
                itemModel = ProductModel(**item)
                #Borrar item con url x e insertar nuevo
            else:
                itemModel = ProductModel(**item)

        try:
            session.add(itemModel)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item

    def hashexist(self, session, hash):
        hashlist = session.execute(
            text("SELECT * FROM productable WHERE hash=:hashtocheck"),
            {"hashtocheck": hash}
            )
        if hashlist.rowcount != 0:
            return True
        else:
            return False

    def urlexist(self, session, urltocheck):
        urllist = session.execute(
            text("SELECT * FROM productable WHERE url=:urlcheck"),
            {"urlcheck": urltocheck]
            )
        if urllist.rowcount != 0:
            return True
        else:
            return False
