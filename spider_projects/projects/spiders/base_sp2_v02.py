import scrapy
import time
import datetime
from random import randrange
from sqlalchemy import text
from projects.items import DescriptionItem, ImgItem, ProductItem
from scrapy.spider import Spider
from scrapy.selector import Selector
from projects.lib.farmazaslib import crea_sesion_db, generar_loader, id_product_from_url, \
                                 id_category_from_url, guarda_status, get_hash, debugPrint, \
                                 debugCategoryXPaths
from scrapy.utils.response import open_in_browser

#** farmaciafrias_sp1_v03.py
#*  @desc       Arana que saca categorias y productos de un ecommerce. La funcion parse es main.
#*  @author     rafa <rafahsolis@gmail.comgmail>
#*  @author     pablo <pabs.ferrari@gmail.com>
#*  @comments   Para cambiar de site modificar xpath en la definicion de variables de clase y buscar @WARNING por el documento
class base_sp2(Spider): #@Warning: Cambiar nombre de clase
    # ** DEFINICION DE VARIABLES **
    name = "Sp2" #@WARNING: Nombre de la arana para scrapy
    ID_site = 3 #@WARNING: id del site en la base de datos. @todo: podria no tener esto, se mira si la url del site existe. Si no se inserta, si si se recupera su id
    local = False #poner en true para lanzar la arana contra URLs en localhost
    nameSp1 = "Sp1" #@WARNING: Nombre de la arana que escrapea las categorias

    #* URLs a las que lanzar si es local o no
    if local:
        allowed_domains = ["farmaciaonlinemadrid.localhost"]#@WARNING
        start_urls = ["http://farmaciaonlinemadrid.localhost"]#@WARNING
        rootpath = "http://farmaciaonlinemadrid.localhost"#@WARNING
    else:
        allowed_domains = ["farmaciaonlinemadrid.com"]#@WARNING
        start_urls = ["http://www.farmaciaonlinemadrid.com"]#@WARNING
        rootpath = "http://www.farmaciaonlinemadrid.com"#@WARNING

    #** DEFINICION DE XPATHS ** #@WARNING todos

    #@WARNING: ProductItem_fields{}: sus campos deben existir en sus relaciones desde models, items y pipelines (este ultimo sOlo a veces)
    ProductItem_fields = {'name' : '//div[@id="primary_block"]/h1/text()',
                          'price': '//span[@id="our_price_display"]/text()',
                          'currency': '//span[@id="our_price_display"]/text()',
                          'available': '//span[@id="quantityAvailable"]/text()',
                          'categoryname': '',#No usar sale por relacion de tablas
                          'cn': '//div[@id="noenestesite"]', #@Warning: No disponible para este site
                          'subcategory': '',#No usar sale por relacion de tablas
                          'url': ''} # sale de response.url

    descItem_fields = {'titulo': '//div[@id="short_description_content"]/p/strong',
                             'texto': '//div[@id="short_description_content"]/text()'}

    imgItem_fields= {'url': '//div[@id="image-block"]/img/@src'}

    descItem_fields = {'titulo': '//div[@class="breadcrumb"]/text()',
                       'subtitulo': '//none',
                       'texto': '//div[@id="short_description_content"]/p'}

    shortdescItem_fields = {'titulo': '//div[@id="short_description_content"]/p/text()',
                            'subtitulo': '//div[@id="short_description_content"]/p/span[0]/strong/text()',
                            'texto': '//div[@id="short_description_content"]/p/span[1]/strong/text()'}
    #@ToDo: Cargar y yield de shortdescItem

    #@WIP: funcion para cargar descripciones



    #** parse(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    #*  @WARNING: esta funcion lleva un time.sleep(randrange(3,6)),si este valor es bajo o nulo podria ser un ataque ilegal y tirar el servidor
    def parse(self, response):
        """ 1.- preparo variables, objetos, conexion BD"""
        self.Session = crea_sesion_db()
        sesion = self.Session()
        try:
            """ 2.- extraer productos de base de datos"""
            # DUDA: aguantara para miles de productos
            productlist = sesion.execute(text("SELECT * FROM productable WHERE id_site=:siteID"),
                {"siteID": self.ID_site})
            cntr = 0
        except:
            debugPrint(logmessage='Error cargando productlist en parse() farmaciafrias_Sp2')
        finally:
            sesion.close()

        for product in productlist:
            time.sleep(randrange(3,6))
            yield scrapy.Request(product[4], callback=self.parse_detalle_producto)
            cntr = cntr + 1

        if cntr < 1:
            debugPrint(cntr, 'No se cargaron categorias para el site en la base de datos \n'
                            'ejecutar: scrapy crawl ' + self.nameSp1)

        sesion.close()
        """ 3.- callback producto a producto mediante parse_producto para sacar la informacion """
 

        """ 4.- cambiamos el estatus de como ha ido la aranya """
        guarda_status()


     #** parse_detalle_producto(self, response);  callback= en parse()
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      Extrae la informacion para cada producto de su pagina de detalle y la guarda en BD
    def parse_detalle_producto(self, response):
        self.total_selector = Selector(response)

        #**BLOQUE DE CODIGO PARA DEBUGIN DE XPATHS
        #open_in_browser(response)
        debugCategoryXPaths(self.total_selector, response,
                            self.ProductItem_fields,
                            self.imgItem_fields, self.descItem_fields)
        debugCategoryXPaths(self.total_selector, response, descItem_fields=self.shortdescItem_fields, printHeader=False)



        #no es necesario pasar el selector, puesto para aclaraciones. ToDo modo factoria a generar_loader()
        if self.total_selector:
            imgLoader = generar_loader(ImgItem(), selector=self.total_selector)
            productLoader = generar_loader(ProductItem(), selector=self.total_selector)
            descLoader = generar_loader(DescriptionItem(), selector=self.total_selector)
            self.cargar_detail_loaders(imgloader=imgLoader, sourceurl=response.url)
            self.cargar_detail_loaders(productloader=productLoader, sourceurl=response.url)
            self.cargar_detail_loaders(descloader=descLoader, sourceurl=response.url)
            yield imgLoader.load_item()
            yield productLoader.load_item()
            yield descLoader.load_item()
        else:
            debugPrint(logmessage='No se creo self.total_selector.xpath en parse_detalle_producto()')


    def cargar_detail_loaders(self, imgloader=None, productloader=None, descloader=None, sourceurl=None):
        """cargar_detail_loaders(imgLoader, productLoader, descLoader)
           carga la informacion correspondiente en cada loader"""
        if productloader:
            #comprueba si existe el hash en la base de datos desde pipelines.py
            #generar prodhash1 igal que en sp1 ToDo: Meter en una funcion de una libreria las generaciones de hash de todas las aranas
            #ToDo: anadir categoria y subcategoria?
            productloader.add_value('cn', u'')
            productloader.add_xpath('name', self.ProductItem_fields['name'])
            productloader.add_value('price', self.total_selector.xpath(self.ProductItem_fields['price']).re(r'\d+.\d+\S'))
            productloader.add_value('currency', self.total_selector.xpath(self.ProductItem_fields['price']).re(r'\s.*'))
            now = datetime.datetime.now()
            productloader.add_value('date_mod', unicode(now.isoformat()))
            productloader.add_value('url', unicode(sourceurl))
            productloader.add_value('id_site', self.ID_site)
            productloader.add_xpath('available', self.ProductItem_fields['available'])
            productloader.add_value('cn', self.total_selector.xpath(self.ProductItem_fields['cn']).re(r'\d+.\d'))
            productloader.add_value('id_category', id_category_from_url(sourceurl))
            #ToDo: Meter en una funcion
            prodhash = get_hash(
                productloader.get_output_value('name') +
                productloader.get_output_value('price') +
                productloader.get_output_value('currency') +
                productloader.get_output_value('available') +
                productloader.get_output_value('url') +
                unicode(self.ID_site)
            )
            productloader.add_value('hash', prodhash)
        if imgloader:
            #ToDo: Meter en libreria
            imgloader.add_value('producturl', unicode(sourceurl))
            imgloader.add_value('source_url', self.total_selector.xpath(self.imgItem_fields['url']).extract()[0]) #no se puede add_xpath, selector diferente al del loader
            imgloader.add_value('id_site', self.ID_site)
            imgloader.add_value('img_type', u'defoult')
            #ToDo: Meter en libreria
            imghash = get_hash(
                imgloader.get_output_value('producturl') +
                imgloader.get_output_value('source_url') +
                imgloader.get_output_value('img_type') +
                unicode(self.ID_site)
            )
            imgloader.add_value('hash', imghash)
            imgloader.add_value('id_product', id_product_from_url(sourceurl))
        if descloader:
            #Cargar el loader ToDo:Meter en una funcion
            #ToDo: WIP cargarDescriptionLoader(descloader, sourceurl)
            descloader.add_value('producturl', unicode(sourceurl))
            descloader.add_xpath('texto', self.descItem_fields['texto'])
            descloader.add_xpath('titulo', self.descItem_fields['titulo'])
            descloader.add_value('desc_type', u'defoult')
            now = datetime.datetime.now()
            descloader.add_value('desc_date', unicode(now.isoformat()))
            #genera hash ToDo: Meter en una funcion
            deschash = get_hash(
                                 descloader.get_output_value('producturl')+
                                 descloader.get_output_value('texto')+
                                 descloader.get_output_value('titulo')+
                                 descloader.get_output_value('desc_type'))
            descloader.add_value('hash', deschash)
            descloader.add_value('id_product', id_product_from_url(sourceurl))







