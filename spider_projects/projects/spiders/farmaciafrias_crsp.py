import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule

from projects.items import SiteItem, CategoryItem, ProductItem, DescItem, imgItem
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose
from scrapy.selector import Selector
from scrapy.http import Request

class FarmaciaFrias(CrawlSpider):
    """Spider for regularly updated www.farmacia-frias.com/es/ site"""

    # Definicion nombre, dominios permitidos y urls de inicio
    name = "FarmaciaFriasCrawl"
    allowed_domains = ["farmacia-frias.com"]
    start_urls = ["http://www.farmacia-frias.com/es/"]
    ID_site = u'FF0001'    
    category_list_xpath = '//*[@id="categories_block_left"]/div/ul/li'

    # anadir item_fields
    CategoryItem_fields = {'url': 'a/@href',
                           'name': 'a/text()',
                           'description': 'a/@title'}   


    def parse(self, response):
        """
        Default callback used by Scrapy to process downloaded responses

        @url farmaciafrias.localhost

        """
        cats_sel = Selector(response)
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
                if field == 'url':
                    Request(cats.xpath(xpath).extract()[0], callback=self.parse_cat)

            loader.add_value('ID_site', self.ID_site)
            #ADD date 
           
            # Carga la categoria en la BD
            loader.load_item()


            #Continuar parseando dentro de las categorias 

            #Necesario importar CrawlSpider, Rule.
       
    #define parse_cat function
    def parse_cat(self, response):
        print('PARSE_CAT')

