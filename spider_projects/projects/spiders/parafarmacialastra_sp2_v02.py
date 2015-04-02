import scrapy
import hashlib
import time
import urlparse
import datetime
from sqlalchemy import text
from projects.items import SiteItem, ProductItem, CategoryItem, DescriptionItem, ImgItem
from projects.farmatorlib import crea_sesion_db, generar_loader, id_product_from_url, id_category_from_url
from scrapy.spider import Spider
from scrapy.selector import Selector
from random import randrange
from scrapy.utils.response import open_in_browser


#ToDo: Comprobar que no se usa ni se usara para eliminarlo y crear las librerias


class parafarmaciaLastra_sp2(Spider):
    #   1.- CAMBIAR name al nombre con el que se lanza
    name = "parafarmacialastra_sp2"

    nameSp1 = "parafarmacialastra_sp1"
    local = False

    #   2.- CAMBIAR allowed_domains, start_urls y rootpath
    if local:
        allowed_domains = ["parafarmacialastra.localhost"]
        start_urls = ["http://parafarmacialastra.localhost"]
        rootpath = "http://parafarmacialastra.localhost"
    else:
        allowed_domains = ["parafarmacialastra.es"]
        start_urls = ["http://www.parafarmacialastra.es/tienda-online.html"]
        rootpath = "http://www.parafarmacialastra.es"

    #  3.- CAMBIAR ID SITE
    ID_site = 2
    
    #   4.- CAMBIAR category_list_xpath y product_list_xpath (DEBUG -01-)
    list_xpath= {'productDetail': '//div[@class="productdetails-view productdetails"]',
                 'subcategory': '',
                 'suburl': '',
                 'subname': '',
                 'catsnochild':'',
                 'catswchild': '',
                 'product': '',
                 'parent': '',
                 'productcategory':''}


    ### 5.- OBTENER XPATHS PARA CategoryItem_fields, ProductItem_fields y subcatloader_fields
    CategoryItem_fields = {'url': '',
                           'name': '',
                           'description': ''}

    ProductItem_fields = {'name': '//div[@class="product-name"]/h1/text()',
                          'price': 'div/div/div/div/div/span[@class="PricesalesPrice"]/text()',
                          'currency': '',
                          'cn': '//div[@class="product-short-description"]/text()',
                          'category': '',
                          'subcategory': '',
                          'url': ''}

    """ ESTE NO SE USA
    subcatloader_fields = {'ID_site': '',
                          'name': '',
                          'parent': '',
                          'url': ''}"""

    imgItem_fields= {'url': '//div[contains(@class,"main-image")]/div/div/a/img/@src'}

    descItem_fields = {'titulo': '//div[@id="productDescription"]//p',
                       'texto': '//div[@class="product-short-description"]/text()'}
            


    def parse(self, response):
        """ 1.- preparo variables, objetos, conexion BD"""
        total_selector = Selector(response)
        self.Session = crea_sesion_db()
        sesion = self.Session()
        """ 2.- extraer productos de base de datos"""
        # DUDA: aguantara para miles de productos
        productlist = sesion.execute(text("SELECT * FROM productable WHERE id_site=:siteID"),
            {"siteID": self.ID_site})
        cntr = 0
        sesion.close()
        for product in productlist:
            #            self.printDebug(product)
            #self.printDebug(product[3], 'url a seguir')
            time.sleep(randrange(3,6))
            yield scrapy.Request(product[4], callback=self.parse_detalle_producto)
            cntr = cntr + 1

        if cntr < 1:
            self.printDebug(cntr, 'No se cargaron categorias para el site\n'
                            'ejecutar: scrapy crawl ' + self.nameSp1 +
                            '\nValor de cntr en "for product in productlist" de parse en parafarmaciaLastra_sp2(Spider)=')

#        self.printDebug(sesion, 'sesion')
        sesion.close()
        """ 3.- callback producto a producto mediante parse_producto para sacar la informacion """
 

        """ 4.- cambiamos el estatus de como ha ido la aranya """
        self.guarda_status()    
 
    def parse_detalle_producto(self, response):
        """ Extrae informacion del producto de su pagina de detalle y actualiza en BD """
        #open_in_browser(response)
        total_selector = Selector(response)
        self.productDetail_sel = total_selector.xpath(self.list_xpath['productDetail'])
        #  Buscando Xpaths, e informacion a rellenar
        # ProductItem
        # r'Name:\s*(.*)'
        #self.printDebug(productDetail_sel.xpath(self.ProductItem_fields['name']).extract(), 'Name')
        #self.printDebug(productDetail_sel.xpath(self.ProductItem_fields['price']).re(r'\d+.\d+\S'), 'Price')
        #self.printDebug(productDetail_sel.xpath(self.ProductItem_fields['price']).re(r'\s.*'), 'Currency')
        #self.printDebug(productDetail_sel.xpath(self.ProductItem_fields['cn'].re(r'\d+.\d')), 'CN')
        # ImgItem
        #self.printDebug(self.fix_url(productDetail_sel.xpath(self.imgItem_fields['url']).extract()[0]), 'imglink')
        # ImgDescriptionItem
        #self.printDebug(productDetail_sel.xpath(self.descItem_fields['titulo']), 'titulo')
        #self.printDebug(productDetail_sel.xpath(self.descItem_fields['texto']).extract(), 'Short Desc')
        #self.printDebug(response.url, 'Scraped url')
        #fin buscando

        #no es necesario pasar el selector, puesto para aclaraciones. ToDo ver si lo quito
        if self.productDetail_sel:
            imgLoader = generar_loader(ImgItem(), selector=self.productDetail_sel)
            productLoader = generar_loader(ProductItem(), selector=self.productDetail_sel)
            descLoader = generar_loader(DescriptionItem(), selector=self.productDetail_sel)
            self.cargar_detail_loaders(imgloader=imgLoader, sourceurl=response.url)
            self.cargar_detail_loaders(productloader=productLoader, sourceurl=response.url)
            self.cargar_detail_loaders(descloader=descLoader, sourceurl=response.url)
            yield imgLoader.load_item()
            yield productLoader.load_item()
            yield descLoader.load_item()
        else:
            self.printDebug(logmessage='No se creo self.productDetail_sel en parse_detalle_producto()')



    def cargar_detail_loaders(self, imgloader=None, productloader=None, descloader=None, sourceurl=None):
        """cargar_detail_loaders(imgLoader, productLoader, descLoader)
           carga la informacion correspondiente en cada loader"""
        if productloader:
            #ToDo: Coger categorias o comprobar si existe hash antiguo y no modificar
            #comprueba si existe el hash en la base de datos
            #generar prodhash1 igal que en sp1 ToDo: Meter en una funcion de una libreria
            #ToDo: anadir categoria y subcategoria
            #ToDo: Cargar el loader
            productloader.add_value('cn', u'')
            productloader.add_xpath('name', self.ProductItem_fields['name'])
            productloader.add_value('price', self.productDetail_sel.xpath(self.ProductItem_fields['price']).re(r'\d+.\d+\S'))
            productloader.add_value('currency', self.productDetail_sel.xpath(self.ProductItem_fields['price']).re(r'\s.*'))
            now = datetime.datetime.now()
            productloader.add_value('date_mod', unicode(now.isoformat()))
            productloader.add_value('url', unicode(sourceurl))
            productloader.add_value('id_site', self.ID_site)
            productloader.add_value('available', u'not used by site')
            productloader.add_value('cn', self.productDetail_sel.xpath(self.ProductItem_fields['cn']).re(r'\d+.\d'))
            productloader.add_value('id_category', id_category_from_url(sourceurl))
            #ToDo: Meter en una funcion
            prodhash = self.get_hash(
                productloader.get_output_value('name') +
                productloader.get_output_value('price') +
                productloader.get_output_value('currency') +
                productloader.get_output_value('url') +
                unicode(self.ID_site)
            )
            productloader.add_value('hash', prodhash)
        if imgloader:
            #ToDo: Meter en libreria
            imgloader.add_value('producturl', unicode(sourceurl))
            imgloader.add_value('source_url', self.productDetail_sel.xpath(self.imgItem_fields['url']).extract()[0]) #no se puede add_xpath, selector diferente al del loader
            imgloader.add_value('id_site', self.ID_site)
            imgloader.add_value('img_type', u'defoult')
            #ToDo: Meter en libreria
            imghash = self.get_hash(
                imgloader.get_output_value('producturl') +
                imgloader.get_output_value('source_url') +
                imgloader.get_output_value('img_type') +
                unicode(self.ID_site)
            )
            imgloader.add_value('hash', imghash)
            #@WIP: sacar funcion que saque id_product de base de datos o de donde sea y lo meta aqui abajo. (from url?)
            imgloader.add_value('id_product', id_product_from_url(sourceurl))
        if descloader:
            #Cargar el loader ToDo:Meter en una funcion
            descloader.add_value('producturl', unicode(sourceurl))
            descloader.add_xpath('texto', self.descItem_fields['texto'])
            descloader.add_xpath('titulo', self.descItem_fields['titulo'])
            descloader.add_value('desc_type', u'defoult')
            now = datetime.datetime.now()
            descloader.add_value('desc_date', unicode(now.isoformat()))
            #genera hash ToDo: Meter en una funcion
            deschash = self.get_hash(
                                 descloader.get_output_value('producturl')+
                                 descloader.get_output_value('texto')+
                                 descloader.get_output_value('titulo')+
                                 descloader.get_output_value('desc_type'))
            descloader.add_value('hash', deschash)



    def hash_exist(self, hash):
        #abre la base de datos
        #busca hash
        #cierra sesion
        #devuelve true/false
        #ToDo: ver si hay que escribirla o se puede usar la del pipeline
        return True





    def get_hash(self, hashseed):
        """ Devuelve un hash md5 unicode generado con hashseed unicode"""
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
            catloader = generar_loader(CategoryItem(), selector=cats)
            cats_dic = {}
            for field, xpath in self.CategoryItem_fields.iteritems():
                if xpath != '':
                    if field == 'url':
                        catloader.add_value(field, urlparse.urljoin(self.rootpath, cats.xpath(xpath).extract()[0]))
                    else:
                        catloader.add_xpath(field, xpath)
                    cats_dic[field] = catloader.get_output_value(field)

            """ guarda la categoria (name, url) en la variable de clase"""
            hash = self.get_hash(unicode(self.ID_site) + cats_dic['name'] + urlparse.urljoin(self.rootpath, cats_dic['url']))
            catloader.add_value('ID_site', self.ID_site) # Comprobar que ID_site sea nullable=False
            cats_dic['ID_site'] = self.ID_site
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
                subcatloader = generar_loader(CategoryItem(), selector=sub)
                subcatloader.add_value('ID_site', self.ID_site)
                subcatloader.add_xpath('name', self.list_xpath['subname'])
                subcatloader.add_value('parent', parent)
                url = sub.xpath(self.list_xpath['suburl']).extract()[0]
                subcatloader.add_value('url', urlparse.urljoin(self.rootpath, url))
                cats_dic['ID_site'] = self.ID_site
                cats_dic['name'] = subcatloader.get_output_value('name')
                cats_dic['url'] = subcatloader.get_output_value('url')
                hash = self.get_hash(self.ID_site + subcatloader.get_output_value('name') + urlparse.urljoin(self.rootpath, subcatloader.get_output_value('url')))
                subcatloader.add_value('hash', hash)
                cats_dic['parent'] = parent
                cats_dic['hash'] = hash
                cats_list.append(cats_dic)
                
             
        yield cats_list
        return 


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
        category= cat_sel.xpath(self.ProductItem_fields['category']).extract()
        subcategory= cat_sel.xpath(self.ProductItem_fields['subcategory']).extract()
        if not category:
            try:
                category= products.xpath(self.list_xpath['productcategory']).extract()[0]
            except:
                self.printDebug(logmessage='Hubo un error cargando el nombre de una categoria en parse_categoria()')

        for product in products:
            prodloader = generar_loader(ProductItem(), selector=product)
            hashseed = ''
            for field, xpath in self.ProductItem_fields.iteritems():
                if xpath:
                    prodloader.add_xpath(field, xpath)
                    hashseed = hashseed + prodloader.get_output_value(field)

            prodloader.add_value('ID_site', self.ID_site)
            hashseed = hashseed + self.ID_site
            prodloader.add_value('hash', unicode(self.get_hash(hashseed)))
            prodloader.add_value('category', category)
            prodloader.add_value('subcategory', subcategory)
            yield prodloader.load_item()


    def fix_url(self, urltofix, rootpathopcional=None):
            if rootpathopcional:
                url = urlparse.urljoin(unicode(rootpathopcional), urltofix)
            else:
                url = urlparse.urljoin(unicode(self.rootpath), urltofix)
            return url


    def printDebug(self, printelement=None, logmessage=''):
        print('\n')
        if logmessage:
            print('>>>>>> Debug:' + logmessage)

        print(printelement)
        print('----------------------- Debug END -----------------------')


