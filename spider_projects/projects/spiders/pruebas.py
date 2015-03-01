import scrapy
from scrapy.spider import Spider

from projects.items import SiteItem, CategoryItem, ProductItem, DescItem, imgItem
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose
from scrapy.selector import Selector
from scrapy.http import Request
import re

class FarmaciaFrias(Spider):

    #Para pruebas en local comentar lineas 18,19 descomentar lineas 16 y 17
    #En local solo funciona el enlace a la categoria 382-facial.html
    #Para pruebas en servidor comentar lineas 16,17 descomentar lineas 18 y 19

    # Definicion nombre, dominios permitidos y urls de inicioi
    name = "prueba"
    local=True
    if local:
        allowed_domains = ["farmaciafrias.localhost"]
        start_urls = ["http://farmaciafrias.localhost"]
    else:
        allowed_domains = ["farmacia-frias.com"]
        start_urls = ["http://www.farmacia-frias.com/es/"]

    ID_site = u'FF0001'    
    category_list_xpath = '//*[@id="categories_block_left"]/div/ul/li'
    category_name = ''
    product_list_xpath = '//*[@id="product_list"]/li'

    # anadir item_fields
    CategoryItem_fields = {'url': 'a/@href',
                           'name': 'a/text()',
                           'description': 'a/@title'}   

    ProductItem_fields = {'name': 'div/h3/a/text()',
                          'price': 'div/div[@class="content_price"]/span/text()',
                          'currency': 'div/div[@class="content_price"]/span/text()',
                          'available': 'div[@class="right_block"]/div[@class="content_price"]/span[@class="availability"]/span[@class="warning_inline"]/text()',
                          'category': '.'}

    def parse(self, response):
        """
        Default callback used by Scrapy to process downloaded responses

        @url farmaciafrias.localhost

        """
        cats_sel = Selector(response)

####
        categorias = cats_sel.xpath(self.category_list_xpath)
        # Recorre las categorias extrayendo informacion
        for cats in categorias:
            loader = ItemLoader(CategoryItem(), selector=cats)

            #Procesado de texto 
            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()

            #Generar item para cada categoria
            for field, xpath in self.CategoryItem_fields.iteritems():
                loader.add_xpath(field, xpath)
#BUENA                if field == 'url':
#BUENA                    yield scrapy.Request(cats.xpath(xpath).extract()[0], callback=self.parse_cat)

            loader.add_value('ID_site', self.ID_site)
            #ADD date 

            # Carga la categoria en la BD
#BUENA            yield loader.load_item()

#Mala esta yield scrapy.Request("http://far... es solo para desarrollo, reemplazar por las BUENAS
            yield scrapy.Request("http://farmaciafrias.localhost/382-facial.html", callback=self.parse_cat)
            
            #Continuar parseando dentro de las categorias 
            #Necesario importar CrawlSpider, Rule.
            #define parse_cat function


    def parse_cat(self, response):
        prod_sel = Selector(response)
        self.cat_name = prod_sel.xpath('//div[@class="breadcrumb"]/span[@class="navigation_page"]/text()').extract()
        product = prod_sel.xpath(self.product_list_xpath)

        for product in product:
            loader= ItemLoader(ProductItem(), selector=product)
            loader.add_value('ID_site', self.ID_site)

            #Procesado del texto
            loader.default_input_processor = MapCompose(unicode.strip)
            loader.default_output_processor = Join()

            #Generar item para cada producto
            for field, xpath in self.ProductItem_fields.iteritems():
                loader.add_xpath(field, xpath)

            loader.add_value('category', self.cat_name)
            yield loader.load_item()  

