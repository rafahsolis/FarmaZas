# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

class SiteItem(Item):
    """Sites container (dictionary-like object) for scraped data
       Fields: ID_site, URL, name, status, date_in, date_check, date_scraped, check_spName,
       scrap_DescName."""
    ID_site = Field()
    URL = Field()
    name = Field()
    status = Field()
    date_in = Field()
    date_check = Field()
    date_scraped = Field()
    check_spName = Field()
    scrap_spName = Field()
    scrap_DescName = Field()


class CategoryItem(Item):
    """Sites container (dictionary-like object) for scraped data
       Fields: ID_category, name, description, url, ID_site"""
    ID_category = Field()
    name = Field()
    description = Field()
    url = Field()
    ID_site = Field()
      


class ProductItem(Item):
    """Product container (dictionary-like object) for scraped data
       Fields: ID_product, name, ID_site, ID_desc, date_in, date_mod, price, currency, available, 
       country, city, postalcode, category"""
    ID_product = Field()
    name = Field()
    ID_site = Field()
    ID_desc = Field()
    date_in = Field()
    date_mod = Field()
    price = Field()
    currency = Field()
    available = Field()
    category = Field()
    hash = Field()

class DescItem(Item):
    """Product container (dictionary-like object) for scraped data
       Fields: ID_desc, text, ID_product, desc_date, desc_type"""
    ID_desc = Field()
    text = Field()
    ID_product = Field()
    desc_date = Field()
    desc_type = Field()


class imgItem(Item):
    """Product container (dictionary-like object) for scraped data
       Fields: ID_img, ID_product, URL_ext, URL_int"""
    ID_img = Field()
    ID_product = Field()
    URL_ext = Field()
    URL_int = Field()
