import scrapy
import hashlib
import time
import urlparse
from scrapy.spider import Spider
from projects.items import CategoryItem, ProductItem
from projects.models import db_connect
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join
from scrapy.selector import Selector
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from random import randrange
from scrapy.contrib.loader.processor import MapCompose
import re

#** base_sp1_v04.py
#*  @desc       Arana que saca categorias y productos de un ecommerce. La funcion parse es main.
#*  @author     rafa <rafahsolis@gmail.comgmail>
#*  @comments   Para cambiar de site modificar xpath en la definicion de variables de clase y buscar @WARNING por el documento
class Base_sp1(Spider): #@Warning: Cambiar nombre de clase
    # ** DEFINICION DE VARIABLES **
    name = "Sp1" #@WARNING: Nombre de la arana para scrapy
    id_site = 3 #@WARNING: id del site en la base de datos. Debe ser INTEGER @todo: podria no tener esto, se mira si la url del site existe. Si no se inserta, si si se recupera su id
    local = False #poner en true para lanzar la arana contra URLs en localhost

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
    #*list_xpath{}: listado general de xpaths. @todo: reordenar por coneptos, tiene popurri de productos y categorias
    list_xpath= {'categoryname': '//*[@id="categories_block_left"]/div/ul/li', #menu completo de lis de las categorias
                 'subcategory': 'ul/li', #grupo de lis que comforman subcategorias dentro del li de la categoria usado en llamada recursiva en getCategorias()
                 'product': '//*[@id="product_list"]/li', #listado completo de lis de productos de una pagina de una categoria
                 'productcategory':'//div[@id="breadcrumb"]/a[1]/text()', #nombre de la categoria cuando navegas por subcategorias. suelen ser breadcrumb o h1,h2,h3...
                 'nextproductpage': '//ul[@class="pagination"]/li[@id="pagination_next"]/a/@href'} # XPath a pagina siguiente en detalle categoria, para paginar los productos.

    #*CategoryItem_fields{}: Listado de xpaths desde el <li> de la categorIa en el menU hasta la informaciOn de la categorIa.
    #*Se usa en crea_lista_categorias_oneloop()
    #@WARNING: sus campos deben existir en sus relaciones desde models, items y pipelines (este ultimo sOlo a veces)
    CategoryItem_fields = {'url': 'a/@href',
                           'name': 'a/text()',
                           'description': '//none'} #no disponible para farmaciaonlinemadrid.

    #*ProductItem_fields{}: Listado de XPaths desde la pagina de categoria a la informacion de cada producto
    #*Se usa en parse_categoria()
    #@WARNING: sus campos deben existir en sus relaciones desde models, items y pipelines (este ultimo sOlo a veces)
    ProductItem_fields = {'name' : 'div[@class="center_block"]/a/@title',
                          'price': 'div[@class="right_block"]/div/span[@class="price"]/text()',
                          'currency': 'div[@class="right_block"]/div/span[@class="price"]/text()',
                          'available': 'div[@class="right_block"]/div/span[@class="availability"]/text()',
                          'categoryname': 'div[@class="center_column"]/h1/text()',
                          'subcategory': 'div[@class="breadcrumb"]/a[1]/@title',# Parent en el caso de farmaciaonlinemadrid
                          'url': 'div[@class="center_block"]/h3/a/@href',
                          'cn': '//none'}

    #** parse(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    #*  @WARNING: esta funcion lleva un time.sleep(randrange(3,6)),si este valor es bajo o nulo podria ser un ataque ilegal y tirar el servidor
    def parse(self, response):
        total_selector = Selector(response) #Selector a partir del resopnse para poder usar busquedas de xpaths
        categorias = self.extrae_arbol(total_selector) #Extraemos las categorias y subcategorias en una lista

        for categoria in categorias:
            cat_loader = self.generar_loader(CategoryItem(), response) #preparamos el ItemLoader (mirar funcion generar_loader y items.py para definir los input y output processors usados para todos los campos a insertar en base de datos que no sean unicode
            self.cargar_loader(cat_loader, **categoria) #metemos los datos extraidos de una categoria en el loader
            yield cat_loader.load_item() #guardamos en base de datos la categoria

            time.sleep(randrange(3,6))

            yield scrapy.Request(categoria['url'], callback=self.parse_categoria) #lanzamos un parse de la URL de la categoria, buscamos obtener las URLs de todos los productos de cada categoria
 
        #@todo: sistema de status
        self.guarda_status()    

    #** get_hash(self, hashseed)
    #*  @params:    hashseed (string)
    #*  @desc:      genera un hash a partir de un string
    #*  @returns:   hashed seed (unicode)
    def get_hash(self, hashseed):
        hash = hashlib.md5()
        hashseed = hashseed.encode('ascii', errors='xmlcharrefreplace')
        hash.update(hashseed)
        hashstring = str(hash.hexdigest())
        return unicode(hashstring)

    #** extrae_arbol(self, total_selector)
    #*  @params:    total_selector (selector con todas las categorias)
    #*  @desc:      extrae las categorias, se utiliza para birfurcar aqui la lOgica de la arana en caso de necesitar otra lOgica frente a la extraccion de categorias
    #*  @returns:    lista de categorias y subcategorias del site
    #*  @relacion   extrae_arbol, saca_menu_completo y getCategorias son 3 funciones que podrian ser la misma. Se ha separado asi para facilitar la adaptacion de logica a otros sites
    def extrae_arbol(self, total_selector):
        categorias = self.saca_menu_completo(total_selector)
        return categorias

    #** saca_menu_completo(self, total_selector)
    #*  @params:    total_selector (selector con todas las categorias)
    #*  @desc:      extrae las categorias
    #*  @relacion   extrae_arbol, saca_menu_completo y getCategorias son 3 funsiones que podrian ser la misma. Se ha separado asi para facilitar la adaptacion de logica a otros sites
    def saca_menu_completo(self, total_selector):
        categorias = total_selector.xpath(self.list_xpath['categoryname'])
        menu_completo = self.getCategorias(categorias)
        return menu_completo

    #** getCategorias(self, categorias, parent=None)
    #*  @params:    categoria (lista), parent (string)
    #*  @desc:      funcion recursiva que recorre un arbol extrayendo la informaciOn de todos los nodos
    #*  @returns:   menu_completo (lista con todas las categorias)
    def getCategorias(self, categorias, parent=None):
        menu_completo = []
        for cat in categorias:
            if len(cat.xpath('*')) == 2: #@WARNING: Esto es logica tailormade para farmacia-frias. Mira si tiene 3 hijos o no (0,1,2) para saber si es subcategoria o no, esto hay que pensarlo con cada site
                menu_completo.append(self.crea_lista_categorias_oneloop(cat)) #mete los datos del nodo (categoria) en la lista menu_completo y en base de datos
                parent = cat.xpath(self.CategoryItem_fields['name']).extract() #cojo esta categoria como parent antes de meterme recursivamente en sus subcategorias
                menu_completo = menu_completo + self.getCategorias(cat.xpath(self.list_xpath['subcategory']), parent) #pasamos los lis de los hijos y el nombre del padre para recorrerla de nuevo
            else:
                #@WARNING: por logica del site si tiene menos de 3 nodos hijos quiere decir que es una categoria sin hijos y guardo su info
                menu_completo.append(self.crea_lista_categorias_oneloop(cat)) #guardo en menu_completo y en base de datos

        return menu_completo

    #** guarda_status(self)
    #*  @params:    void
    #*  @desc:      guarda en base de datos el status final de cOmo ha ido el scrapeo
    #*  @todo:      entera
    def guarda_status(self):
        print "todo: guardar status"
        """ guarda en bbdd en sites el status accionable (a1-finishedOK, a1-failed,...)"""
        """ guarda en log el status """

    #** crea_lista_categorias_oneloop(self, categoria, parent)
    #*  @params:    categoria (selector con la categoria a extraer), parent (su parent si lo tiene)
    #*  @returns;   cats_dic (dict con la categoria insertada)
    #*  @desc:      extrae los datos del nodo (categoria) seleccionado, los guarda en la base de datos y devuelve un diccionario con la categoria insertada
    # @todo: el catloader se usa para rellenar el diccionario, no tiene sentido, mejor rellenar el diccionario del tiron y nunca usar catloader aqui pues no quiere guardar en db ni tampoco es una variable global
    def crea_lista_categorias_oneloop(self, categoria, parent=''):
        catloader = self.generar_loader(CategoryItem(), selector=categoria)
        cats_dic = {}
        for field, xpath in self.CategoryItem_fields.iteritems():
            if xpath != '':
                if field == 'url':
                    catloader.add_value(field, urlparse.urljoin(self.rootpath, categoria.xpath(xpath).extract()[0]))
                else:
                    catloader.add_xpath(field, xpath)

                cats_dic[field] = catloader.get_output_value(field)

        hash = self.get_hash(str(self.id_site) + cats_dic['name'] + urlparse.urljoin(self.rootpath, cats_dic['url']))

        cats_dic['hash'] = hash
        cats_dic['id_site'] = self.id_site
        catloader.add_value('hash', hash)
        catloader.add_value('id_site', self.id_site) # Comprobar que id_site sea nullable=False
        if parent != None:
            catloader.add_value('parent', unicode(parent))
            cats_dic['parent'] = unicode(parent)

        return cats_dic

    #** parse_categoria(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana que escrapea una categoria para sacar los productos de dentro (solo nombres y links principalmente) para luego nutrir a la siguiente arana
    #*  @WARNING: esta funcion lleva un time.sleep(randrange(3,6)),si este valor es bajo o nulo podria ser un ataque ilegal y tirar el servidor
    def parse_categoria(self, response):
        cat_sel= Selector(response)
        products= cat_sel.xpath(self.list_xpath['product'])
        category= cat_sel.xpath(self.ProductItem_fields['categoryname']).extract()
        subcategory= cat_sel.xpath(self.ProductItem_fields['subcategory']).extract()

        id_category = self.id_category_from_url(response.url) #Llamada a bbdd para sacar de categorytable el id desde la url

        if not category: #si ha entrado aqui sin tenerla la recargamos
            category= cat_sel.xpath(self.ProductItem_fields['categoryname']).extract()

        for product in products:
            prodloader = self.generar_loader(ProductItem(), selector=product)
            for field, xpath in self.ProductItem_fields.iteritems():
                if xpath:
                    if field == 'url':
                        produrl = self.fix_url(product.xpath(xpath).extract()[0])
                        prodloader.add_value(field, produrl)
                    else:
                        prodloader.add_xpath(field, xpath)

            prodloader.add_value('id_site', self.id_site)
            prodloader.add_value('id_category', id_category)
            prodloader.add_value('categoryname', category)
            prodloader.add_value('subcategory', subcategory)
            prodloader.add_value('cn', u'not available') #@Warning no lo coge para farmaciaonlinemadrid
            prodhash1 =self.get_hash(
                prodloader.get_output_value('name')+
                prodloader.get_output_value('price')+
                prodloader.get_output_value('available')+
                prodloader.get_output_value('url')
            )
            prodloader.add_value('hash', prodhash1)
            #ToDo paginacion, este site de momento no tiene productos suficientes para necesitarlo
            yield prodloader.load_item()

        # WARNING: Paginador taylormade
        next = cat_sel.xpath(self.list_xpath['nextproductpage']).extract()
        if next:
            yield scrapy.Request('http://' + self.rootpath + next[0], callback=self.parse_categoria)

    #** fix_url(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    def fix_url(self, urltofix, rootpathopcional=None):
            #self.printDebug(urltofix, 'URL TO FIX')
            if rootpathopcional:
                url = urlparse.urljoin(unicode(rootpathopcional), urltofix)
            else:
                url = urlparse.urljoin(unicode(self.rootpath), urltofix)
            return url

    #** id_category_from_url(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    def id_category_from_url(self, url):
        self.abre_sesion_db()
        sesion = self.Session()
        url = re.sub(r'\?.*', '', url) # Elimina el parametro de paginacion al buscar la url de la categoria en categoritable
        """ Buscar url en categorytable """
        category_row = sesion.execute(text("SELECT * FROM categorytable WHERE url=:searchurl;"),
            {"searchurl": url})
        sesion.close()
        for r in category_row:
            id=r[0]
        return id

    #** generar_loader(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    def generar_loader(self, item, response=None, selector=None, input_processor=MapCompose(unicode.strip), output_processor=Join()):
        """ Devuelve un loader para el (item, selector=, input_processor=, output_processor=) 
            los parametros con = son opcionales"""
        if selector:
            loader = ItemLoader(item, selector=selector)
        elif response:
            selector = Selector(response)
            loader = ItemLoader(item, selector)

        loader.default_input_processor = input_processor
        loader.default_output_processor = output_processor
        return loader

    #** abre_sesion_db(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    def abre_sesion_db(self):
        """ Conecta a la base de datos y devuelve una sesion
        ussage: newSession = crea_session_db()"""
        engine = db_connect()
        self.Session = sessionmaker(bind=engine)
        return

    #** cargar_loader(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    def cargar_loader(self, loader, *args, **kwargs):
        """ Carga un diccionario en un loader 
            ussage cargar_loader(loader, {clave:'valor', clave:'valor', ...})"""
        for field, value in kwargs.iteritems():
            loader.add_value(field, value)

    #** printDebug(self, response)
    #*  @params:    response (la respuesta del scrapy tras el GET, POST,...)
    #*  @desc:      es el "main()" de la arana
    def printDebug(self, printelement=None, logmessage=''):
        print('\n')
        if logmessage:
            print('>>>>>> Debug:' + logmessage)

        print(printelement)
        print('----------------------- Debug END -----------------------')