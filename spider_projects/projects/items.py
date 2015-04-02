# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.loader.processor import MapCompose, Join

def integer_to_string(value):
    a = unicode(str(value))
    return unicode(value)

def string_to_integer(value):
    return int(value)


class SiteItem(Item):
    """Sites container (dictionary-like object) for scraped data
       Fields: id_site, URL, name, status, date_in, date_check, date_scraped, check_spName,
       scrap_DescName."""
    id = Field(input_processor=MapCompose(integer_to_string), output_processor=string_to_integer)
    name = Field()
    url = Field()
    date_in = Field()
    sp1_name = Field()
    sp1_status = Field()
    sp2_name = Field()
    sp2_status = Field()
    check_spname = Field()
    last_update = Field()
    error_log = Field()
    hash = Field()
    cp = Field()
    ciudad = Field()
    provincia = Field()
    pais = Field()
    guardias = Field()
    street = Field()
    hash = Field()


class CategoryItem(Item):
    """Sites container (dictionary-like object) for scraped data
       Fields: ID_category, name, description, url, id_site"""
    id = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_site = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    name = Field()
    description = Field()
    parent = Field()
    url = Field()
    hash = Field()      


class ProductItem(Item):
    """Product container (dictionary-like object) for scraped data
       Fields: ID_product, name, id_site, ID_desc, date_in, date_mod, price, currency, available, 
       country, city, postalcode, category, subcategory, hash"""
    id = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_category = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_site = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_desc = Field()
    name = Field()
    url = Field()
    date_in = Field()
    date_mod = Field()
    price = Field()
    currency = Field()
    available = Field()
    categoryname = Field() #eliminar (id_category)
    subcategory = Field() #eliminar (id_category)
    cn = Field()
    hash = Field()


class DescriptionItem(Item):
    """Product container (dictionary-like object) for scraped data
       Fields: ID_desc, text, ID_product, desc_date, desc_type"""
    id = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_product = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    titulo = Field()
    subtitulo = Field()
    texto = Field()
    producturl = Field()
    desc_date = Field()
    desc_type = Field()
    id_site = Field()
    hash = Field()


class ImgItem(Item):
    """Product container (dictionary-like object) for scraped data
       Fields: ID_img, ID_product, URL_ext, URL_int"""

    id = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_product = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    id_site = Field(input_processor=MapCompose(integer_to_string), output_processor=MapCompose(string_to_integer))
    producturl = Field()
    size = Field()
    source_url = Field()
    internal_url = Field()
    img_type = Field()
    hash = Field()