# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from models import CategoryModel, db_connect, create_category_table, ProductModel
from items import CategoryItem, ProductItem

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
