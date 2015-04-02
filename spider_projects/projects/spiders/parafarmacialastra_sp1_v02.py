import scrapy
import hashlib
import time
import urlparse
from scrapy.spider import Spider
from projects.items import SiteItem, CategoryItem, ProductItem
from projects.models import db_connect
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose
from scrapy.selector import Selector
from random import randrange


class ParafarmaciaLastra_sp04(Spider):
#   1.- CAMBIAR name al nombre con el que se lanza  
    name = "parafarmacialastra_sp1"
    local = False
    
#   2.- CAMBIAR allowed_domains Y start_urls 
    if local:
        allowed_domains = ["parafarmacialastra.localhost"]
        start_urls = ["http://parafarmacialastra.localhost"]
        rootpath = "http://parafarmacialastra.localhost"
    else:
        allowed_domains = ["parafarmacialastra.es"]
        start_urls = ["http://www.parafarmacialastra.es/tienda-online.html"]
        rootpath = "http://www.parafarmacialastra.es"

#  3.- CAMBIAR ID SITE
    id_site = 2
    
#   4.- CAMBIAR category_list_xpath y product_list_xpath (DEBUG -01-)
    list_xpath= {'category': '//*[@class="VMmenu menu nav"]',
                 'subcategory': 'ul/li',
                 'suburl': 'div/a/@href',
                 'subname': 'div/a/text()',
                 'catsnochild':'li[not(contains(@class, "hasChild"))]',
                 'catswchild': 'li[contains(@class, "hasChild")]',
                 'product': '//div[@class="component"]/div/div/div[contains(@class, "product")]',
                 'parent': 'div/a/text()',
                 'productcategory':'//div[@class="component"]/div/div/h3/text()'}


### 5.- OBTENER XPATHS PARA CategoryItem_fields, ProductItem_fields y subcatloader_fields
    CategoryItem_fields = {'url': 'div/a/@href',
                           'name': 'div/a/text()',
                           'description': ''}

    ProductItem_fields = {'name': 'div/div[contains(@class, "product-detail")]/a/text()',
                          'price': '',
                          'currency': '',
                          'available': '',
                          'cn': '',
                          'categoryname': '//ul[@class="breadcrumb"]/li[3]/a/text()',
                          'subcategory': '//ul[@class="breadcrumb"]/li[4]/span/text()',
                          'url': 'div/div[contains(@class, "product-detail")]/a/@href'}


    subcatloader_fields = {'id_site': '',
                          'name': '',
                          'parent': '',
                          'url': ''}

    def parse(self, response):
        """ 1.- preparo variables, objetos,..."""
        total_selector = Selector(response)

        """ 2.- extraer categorias del arbol"""
        categorias = self.extrae_arbol(total_selector)
        for categoria in categorias:
            """ Cargar las categorias en la base de datos """
            cat_loader = self.generar_loader(CategoryItem(), response)
            self.cargar_loader(cat_loader, **categoria)
            yield cat_loader.load_item()             
    
            """ 3.- callback categoria a categoria mediante parse_categoria para sacar los products (name, url) """
            #time.sleep(randrange(3,6))
            yield scrapy.Request(categoria['url'], callback=self.parse_categoria)
 

        """ 4.- cambiamos el estatus de como ha ido la aranya """
        self.guarda_status()    


    def get_hash(self, hashseed):
        hash = hashlib.md5()
        hashseed = hashseed.encode('ascii', errors='xmlcharrefreplace')
        hash.update(hashseed)
        hashstring = str(hash.hexdigest())
        return unicode(hashstring)


    def extrae_arbol(self, total_selector):
        """ 2.1. saca el menu completo """
        categorias = self.saca_menu_completo_hijos_nohijos(total_selector)
        return categorias


    def guarda_status(self):
        print "todo: guardar status"
        """ guarda en bbdd en sites el status accionable (a1-finishedOK, a1-failed)"""
        """ guarda en log el status """


    def saca_menu_completo_hijos_nohijos(self, total_selector):
        """  Saca el identificador de lis del menu, si tiene hijos o no y el identificador de extracciones 
             (name y url) de variables de clase self.list_xpath y self.CategoryItems_Field """
        categorias = total_selector.xpath(self.list_xpath['category'])
        catsnochild = categorias.xpath(self.list_xpath['catsnochild'])
        catswchild = categorias.xpath(self.list_xpath['catswchild'])
        catsnochild_list = self.crea_lista_categoria_nchild(catsnochild)
        catswchild_list = self.crea_lista_categoria_wchild(catswchild)
        menu_completo = self.suma_listas(catsnochild_list, catswchild_list)
        return menu_completo


    def crea_lista_categoria_nchild(self, categoria_sin_hijos):
        cats_list = []
        for cats in categoria_sin_hijos:
            catloader = self.generar_loader(CategoryItem(), selector=cats)
            cats_dic = {}
            for field, xpath in self.CategoryItem_fields.iteritems():
                if xpath != '':
                    if field == 'url':
                        catloader.add_value(field, urlparse.urljoin(self.rootpath, cats.xpath(xpath).extract()[0]))
                    else:
                        catloader.add_xpath(field, xpath)
                    cats_dic[field] = catloader.get_output_value(field)
                else:
                    catloader.add_value(field, u'')

            """ guarda la categoria (name, url) en la variable de clase"""
            hash = self.get_hash(unicode(self.id_site) + cats_dic['name'] + urlparse.urljoin(self.rootpath, cats_dic['url']))
            catloader.add_value('id_site', self.id_site) # Comprobar que id_site sea nullable=False
            cats_dic['id_site'] = self.id_site
            catloader.add_value('hash', hash)
            cats_dic['hash'] = hash
            cats_list.append(cats_dic)
        yield cats_list


    def crea_lista_categoria_wchild(self, categoria_con_hijos):
        """ Devuelve lista de diccionarios 'json' {'nombre categoria': 'url'"""
        cats_dic = {}
        cats_list = []

        for cats in categoria_con_hijos:
            parent = cats.xpath(self.list_xpath['parent']).extract()[0]
            for sub in cats.xpath(self.list_xpath['subcategory']):
                cats_dic={}
                subcatloader = self.generar_loader(CategoryItem(), selector=sub)
                subcatloader.add_value('id_site', self.id_site)
                subcatloader.add_xpath('name', self.list_xpath['subname'])
                subcatloader.add_value('parent', parent)
                url = sub.xpath(self.list_xpath['suburl']).extract()[0]
                subcatloader.add_value('url', urlparse.urljoin(self.rootpath, url))
                cats_dic['id_site'] = self.id_site
                cats_dic['name'] = subcatloader.get_output_value('name')
                cats_dic['url'] = subcatloader.get_output_value('url')
                hash = self.get_hash(str(self.id_site) + subcatloader.get_output_value('name') + urlparse.urljoin(self.rootpath, subcatloader.get_output_value('url')))
                subcatloader.add_value('hash', hash)
                cats_dic['parent'] = parent
                cats_dic['hash'] = hash
                cats_list.append(cats_dic)
             
        yield cats_list


    def suma_listas(self, lista1, lista2):
        # OJO ALGO RARO HAY AQUI LISTA DENTRO DE LISTA 
        listaSuma = []
        for i in lista1:
            for j in i: 
                listaSuma.append(j)
        
        for k in lista2:
            for l in k:
                listaSuma.append(l)
        
        return listaSuma


    def parse_categoria(self, response):
        cat_sel= Selector(response)
        products= cat_sel.xpath(self.list_xpath['product'])
        category= cat_sel.xpath(self.ProductItem_fields['categoryname']).extract()
        subcategory= cat_sel.xpath(self.ProductItem_fields['subcategory']).extract()
        if not category:
            try:
                category= products.xpath(self.list_xpath['productcategory']).extract()[0]
            except:
                self.printDebug(logmessage='Hubo un error cargando el nombre de una categoria en parse_categoria()')

        for product in products:
            prodloader = self.generar_loader(ProductItem(), selector=product)
            for field, xpath in self.ProductItem_fields.iteritems():
                if xpath:
                    if field == 'url':
                        produrl = self.fix_url(product.xpath(xpath).extract()[0])
                        prodloader.add_value(field, produrl)
                    else:
                        prodloader.add_xpath(field, xpath)
                else:
                    prodloader.add_value(field, u'')

            prodloader.add_value('id_site', self.id_site)
            prodloader.add_value('id_category', self.id_category_from_url(response.url))
            prodloader.add_value('categoryname', category)
            prodloader.add_value('subcategory', subcategory)
            prodhash1 =self.get_hash(
                prodloader.get_output_value('name')+
                prodloader.get_output_value('price')+
                prodloader.get_output_value('available')+
                prodloader.get_output_value('url')
            )
            prodloader.add_value('hash', prodhash1)
            #ToDo paginacion, este site de momento no tiene productos suficientes para necesitarlo
            yield prodloader.load_item()

    def fix_url(self, urltofix, rootpathopcional=None):
            #self.printDebug(urltofix, 'URL TO FIX')
            if rootpathopcional:
                url = urlparse.urljoin(unicode(rootpathopcional), urltofix)
            else:
                url = urlparse.urljoin(unicode(self.rootpath), urltofix)
            return url


    def generar_loader(self, item, response=None, selector=None, input_processor=MapCompose(unicode.strip), output_processor=Join()):
        """ Devuelve un loader para el (item, selector=, input_processor=, output_processor=) 
            los parametros con = son opcionales"""
        if selector:
            loader = ItemLoader(item, selector=selector)
        elif response:
            selector = Selector(response)
            loader = ItemLoader(item, selector)
        try:
            loader.default_input_processor = input_processor
            loader.default_output_processor = output_processor
        except:
            self.printDebug('Fallo en la generacion del loader en generar_loader()')
 
        return loader


    def cargar_loader(self, loader, *args, **kwargs):
        """ Carga un diccionario en un loader 
            ussage cargar_loader(loader, {clave:'valor', clave:'valor', ...})"""
        for field, value in kwargs.iteritems():
            loader.add_value(field, value)

    #ToDo: implementar desde projects.lib.ftlib
    def id_category_from_url(self, url):
        self.abre_sesion_db()
        sesion = self.Session()

        """ Buscar url en categorytable """
        category_row = sesion.execute(text("SELECT * FROM categorytable WHERE url=:searchurl;"),
            {"searchurl": url})
        sesion.close()
        for r in category_row:
            id=r[0]
        return id

    #ToDo: implementar desde projects.lib.ftlib
    def abre_sesion_db(self):
        """ Conecta a la base de datos y devuelve una sesion
        ussage: newSession = crea_session_db()"""
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)
        return

    #ToDo: Implementar desde projects.lib.ftlib debugPrint
    def printDebug(self, printelement=None, logmessage=''):
        print('\n')
        if logmessage:
            print('>>>>>> Debug:' + logmessage)

        print(printelement)
        print('----------------------- Debug END -----------------------')


