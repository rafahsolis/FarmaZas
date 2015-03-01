import scrapy
from scrapy.spider import Spider

from projects.items import SiteItem, CategoryItem, ProductItem, DescItem, imgItem
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose
from scrapy.selector import Selector
from scrapy.http import Request
import hashlib

class FarmaciaFrias(Spider):

    #Para pruebas en servidor poner variable local = False 

    # Definicion nombre, dominios permitidos y urls de inicio

    findb_01= True
    findb_02= True
    findb_03= True
    findb_04= True
    findb_05= False
    findb_06= False
### 1.- CAMBIAR name al nombre con el que se lanza  

    name = "lastradebug"
    local= False

### 2.- CAMBIAR allowed_domains Y start_urls 
    if local:
        allowed_domains = ["parafarmacialastra.localhost"]
        start_urls = ["http://parafarmacialastra.localhost"]
    else:
        allowed_domains = ["parafarmacialastra.es"]
        start_urls = ["http://www.parafarmacialastra.es/tienda-online.html"]
        rootpath = "http://www.parafarmacialastra.es"
### 3.- CAMBIAR ID SITE
    ID_site = u'PF0001'    

### 4.- CAMBIAR category_list_xpath y product_list_xpath (DEBUG -01-)
    category_list_xpath = '//ul[@id="VMmenu19_08546"]'
    subcat_list_xpath = ''
    ID_category = ''
    subcat_name=''
    product_list_xpath = ''

### 5.- OBTENER XPATHS PARA CategoryItem_fields (DEBUG -02-)
    CategoryItem_fields = {'url': '',
                           'name': '',
                           'description': ''}   


    ProductItem_fields = {'name': '',
                          'price': '',
                          'currency': '',
                          'available': '',
                          'url': ''}


    def get_hash(self, hashseed):
        hash = hashlib.md5()
        hashseed = hashseed.encode('ascii', errors='xmlcharrefreplace')
        hash.update(hashseed)
        hashstring = str(hash.hexdigest())
        return hashstring


    def parse(self, response):
        """
        Default callback used by Scrapy to process downloaded responses

        @url farmaciafrias.localhost

        """
        cats_sel = Selector(response)
#### DEBUG -01- ####

#LOCALIZAR EL XPATH A LA LISTA DE CATEGORIAS
#- START
#        self.cat_list_xpath= '//*[@class="VMmenu menu nav"]/li'
        self.cat_list_xpath= '//*[@class="VMmenu menu nav"]'
        if not self.findb_01:
            print('************* DEBUG -01- START *************')
            print('cat_list_xpath: ', self.cat_list_xpath) 
            print('cats_sel.xpath(self.cat_list_xpath)')
            print(cats_sel.xpath(self.cat_list_xpath)) 
            print('cats_sel.xpath(self.cat_list_xpath).extract()')
            print(cats_sel.xpath(self.cat_list_xpath).extract())
            print('************* DEBUG -01- END *************')
            exit('DEBUG -01-')
        else:
            categorias = cats_sel.xpath(self.cat_list_xpath) 
#- END
#*AL OBTENER EL XPATH DESCOMENTAR  #*        self.cat_list_xpath = 'INTRODUCIR XPATH'
                                   #*        self.findb01= True
                                                       
#### DEBUG -01- ####
        
#### DEBUG -02- ####
# OBTENER LOS XPATH PARA LAS CATEGORIAS CON HIJOS Y SIN HIJOS POR SEPARADO
#- START
         # INTRODUCIR LOS XPATH, CUANDO ESTEN OK PONER self.finddb_02 = True

###### cambiar por self.subcat y self.cat _list_xpath
        catsnochildxpath = 'li[not(contains(@class, "hasChild"))]'
        catswchildxpath = 'li[contains(@class, "hasChild")]'
        if not self.findb_02:
            print('************* DEBUG -02- START *************')

            print('CATEGORIAS SIN HIJOS')
            print(categorias.xpath(catsnochildxpath).extract())
            print('CATEGORIAS CON HIJOS')
            print(categorias.xpath(catswchildxpath).extract())
            print('************* DEBUG -02- START *************')
            exit('DEBUG -02-')
        else:
            catsnochild = categorias.xpath(catsnochildxpath)
            catswchild = categorias.xpath(catswchildxpath)
#-END
#### DEBUG -03- ####
#EXTRAER CATEGORIAS SIN HIJOS Y SUS PRODUCTOS
        self.CategoryItem_fields['url'] = 'div/a/@href'
        self.CategoryItem_fields['name'] = 'div/a/text()'
        
        if not self.findb_03:
            print('************* DEBUG -03- START *************')        
            print('URL: ', catsnochild.xpath(self.CategoryItem_fields['url']).extract())
            print('name', catsnochild.xpath(self.CategoryItem_fields['name']).extract())
            print('*************  DEBUG -03- END  *************')
            exit('DEBUG -03-')
#-END
#### DEBUG -03- ####

#### DEBUG -04- ####
#- START
        for cats in catsnochild:
            if not self.findb_04:
                print('************* DEBUG -04- START *************')
                print(cats.xpath(self.CategoryItem_fields['name']).extract()[0])
                print(self.rootpath + cats.xpath(self.CategoryItem_fields['url']).extract()[0])
                for field, xpath in self.CategoryItem_fields.iteritems():
                    if xpath:
                        print(xpath)
                        print(cats.xpath(xpath).extract())
            else:
                catloader= ItemLoader(CategoryItem(), selector=cats)
                catloader.default_input_processor = MapCompose(unicode.strip)
                catloader.default_output_processor = Join()
                hashseed= ''
                for field, xpath in self.CategoryItem_fields.iteritems():
                    if xpath != '':
                        catloader.add_xpath(field, xpath)
                    if not self.local:
                        if field == 'url':
                            self.ID_category = catloader.get_output_value('name')
                            yield scrapy.Request(self.rootpath + cats.xpath(xpath).extract()[0], callback=self.parse_cat)
                            if self.findb_06 == False:
                                hashseed = hashseed + catloader.get_output_value(field)
                                hashseed = hashseed + self.ID_site
                                catloader.add_value('ID_site', self.ID_site)
                                catloader.add_value('hash', unicode(self.get_hash(hashseed)))
                                yield catloader.load_item()
                                exit('DEBUG -05-')

                    hashseed = hashseed + catloader.get_output_value(field)        
                hashseed = hashseed + self.ID_site
                catloader.add_value('ID_site', self.ID_site)
                catloader.add_value('hash', unicode(self.get_hash(hashseed)))
                yield catloader.load_item()
                hashseed= ''
#-END
#### DEBUG -04- ####
       

#### DEBUG -05 - ####
#- START
# OBTENER XPATH INFORMACION PRODUCTOS
    def parse_cat(self, response):
        self.product_list_xpath = '//div[@class="component"]/div/div/div[contains(@class, "product")]'

        self.ProductItem_fields['name']= 'div/div[contains(@class, "product-detail")]/a/text()'
        self.ProductItem_fields['price']= 'div/div[@class="product-addtocartbar"]/div[contains(@id, "productPrice")]/div[@class="PricesalesPrice"]/span/text()'
        self.ProductItem_fields['currency']='div/div[@class="product-addtocartbar"]/div[contains(@id, "productPrice")]/div[@class="PricesalesPrice"]/span/text()'
#utilizado available para C.N.
        self.ProductItem_fields['available']= 'div/div[contains(@class, "product-detail")]/div[@class="product-s-desc"]/p/text()'
        self.ProductItem_fields['url']= 'div/div[contains(@class, "product-detail")]/a/@href'

        cat_sel= Selector(response)
        products= cat_sel.xpath(self.product_list_xpath)
        if not self.findb_05:
            print('************* DEBUG -05- START *************')
            print('XPATH:')
            print(self.product_list_xpath)
            print('EXTRACT')
            print(products.extract())
            print('\n')
            print('************ PRODUCT ITEM FIELDS ***********')
            print('\n') 
            for product in products:
                print('\n')
                for field, xpath in self.ProductItem_fields.iteritems():
                        print(field, xpath)
                        if xpath:
                            print(field + ': ',  product.xpath(xpath).extract())

            print('************* DEBUG -05- END *************')
        elif self.findb_05:
            products = cat_sel.xpath(self.product_list_xpath)	
#- END
#### DEBUG -05 - ####


#### DEBUG -06- ####
# OBTENER subcategorias
#- START
            self.findb_06 = False 
            if not self.findb_06:
                print('************* DEBUG -06- START *************')
                print('************* DEBUG -06- END *************')

#- END
#### DEBUG -05- ####



#            loader = ItemLoader(CategoryItem(), selector=cats)

            #Procesado de texto 
#            loader.default_input_processor = MapCompose(unicode.strip)
#            loader.default_output_processor = Join()

#            hashseed = ''
#            #Generar item para cada categoria
#            for field, xpath in self.CategoryItem_fields.iteritems():
#                loader.add_xpath(field, xpath)
#                if not self.local:
#                    if field == 'url':
#                        yield scrapy.Request(cats.xpath(xpath).extract()[0], callback=self.parse_cat)
#                hashseed = hashseed + loader.get_output_value(field)
#            hashseed = hashseed + self.ID_site
#            hash = hashlib.md5()
#            hashseed = hashseed.encode('ascii', errors='xmlcharrefreplace')
#            hash.update(hashseed)
#            hashstring = str(hash.hexdigest())
#            loader.add_value('hash', unicode(hashstring))
#            loader.add_value('ID_site', self.ID_site)
            #ADD date 

            # Carga la categoria en la BD
#            yield loader.load_item()
#            if self.local:
### 6-(OPCIONAL SOLO SI EN LOCAL) OBTENER ENLACE A PAGINA CATEGORIA EN LOCAL
     
#                yield scrapy.Request("http://farmaciafrias.localhost/382-facial.html", callback=self.parse_cat)

#    def parse_cat(self, response):
#        prod_sel = Selector(response)
#        self.cat_name = prod_sel.xpath('//div[@class="breadcrumb"]/span[@class="navigation_page"]/text()').extract()
#        productos = prod_sel.xpath(self.product_list_xpath)
#        for product in productos:
#            loader= ItemLoader(ProductItem(), selector=product)
#            loader.add_value('ID_site', self.ID_site)
#
#            #Procesado del texto
#            loader.default_input_processor = MapCompose(unicode.strip)
#            loader.default_output_processor = Join()
#
#            hashseed = ''
#            #Generar item para cada producto
#            for field, xpath in self.ProductItem_fields.iteritems():
#                loader.add_xpath(field, xpath)
#                hashseed = hashseed + loader.get_output_value(field)          
#            hash = hashlib.md5()
#            hashseed=hashseed.encode('ascii', errors='xmlcharrefreplace')
#            hash.update(hashseed)
#            hashstring= str(hash.hexdigest())
#            loader.add_value('hash', unicode(hashstring))
#            loader.add_value('category', self.cat_name)
#            yield loader.load_item()  
#
#        next = prod_sel.xpath('//div[@id="center_column"]/div[@class="content_sortPagiBar"]/div[@id="pagination_bottom"]/ul/li[@class="pagination_next"]/a/@href').extract()
#
#        if next:
#            yield scrapy.Request('http://www.farmacia-frias.com' + next[0], callback=self.parse_cat)




