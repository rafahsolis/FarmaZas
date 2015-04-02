
from projects.models import db_connect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose
from scrapy.selector import Selector
import hashlib
import urlparse

#** farmazaslib.py
#*  @desc       Libreria con funciones para las aranas.
#*  @author     Rafa <rafahsolis@gmail.comgmail>
#*  @comments   Importar desde al arana para acceder a las funciones

#ToDo: Input output processors para los id
#ToDo: implementar parametro opcional tabla y campo (buscar campo en tabla)
def id_category_from_url(url):
    id = 0
    Session = crea_sesion_db()
    sesion = Session()

    try:
        """ Buscar url en categorytable """
        category_row = sesion.execute(text("SELECT * FROM categorytable WHERE url=:searchurl;"),
                                      {"searchurl": url})

        for r in category_row:
                id=r[0]
    except:
        id=''
        debugPrint(logmessage='Error en id_category_from_url')
    finally:
        sesion.close()
    return id


def id_product_from_url(url):
    Session = crea_sesion_db()
    sesion = Session()

    try:
        """ Buscar url en product """
        product_row = sesion.execute(text("SELECT * FROM productable WHERE url=:searchurl;"),
            {"searchurl": url})

        for r in product_row:
            id=r[0]
    except:
        debugPrint(logmessage='Error en id_product_from_url')
        id=0
    finally:
        sesion.close()
    return id


def crea_sesion_db():
    """ Conecta a la base de datos y devuelve una sesion
    ussage: newSession = crea_session_db()"""
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    return Session


def debugPrint(printelement=None, logmessage=''):
        print('\n')
        if logmessage:
            print('>>>>>> Debug:' + logmessage)

        print(printelement)
        print('----------------------- Debug END -----------------------')


def generar_loader(item, response=None, selector=None, input_processor=MapCompose(unicode.strip), output_processor=Join()):
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
        debugPrint('Fallo en la generacion del loader en generar_loader()')
    return loader


def guarda_status():
    print "todo: guardar status"
    # ToDo guarda en bbdd en sites el status accionable (a1-finishedOK, a1-failed)
    # guarda en log el status


def cargar_category_loader(self, loader, *args, **kwargs):
    """ Carga un diccionario en un loader
        ussage cargar_loader(loader, {clave:'valor', clave:'valor', ...})"""
    for field, value in kwargs.iteritems():
        loader.add_value(field, value)


def get_hash(hashseed):
    """ Devuelve un hash md5 unicode generado con hashseed unicode"""
    hash = hashlib.md5()
    hashseed = hashseed.encode('ascii', errors='xmlcharrefreplace')
    hash.update(hashseed)
    hashstring = str(hash.hexdigest())
    return unicode(hashstring)


def fix_url(urltofix, rootpathopcional=None):
    if rootpathopcional:
        url = urlparse.urljoin(unicode(rootpathopcional), urltofix)
    else:
        url = urlparse.urljoin(unicode(''), urltofix)
    return url


def debugCategoryXPaths(total_selector, response, ProductItem_fields=None, imgItem_fields=None, descItem_fields=None, printHeader=True):
    #  Buscando Xpaths, e informacion a rellenar
    # ProductItem
    if printHeader:
        print('**************Mostrando resultados para los XPath introducidos***************')
        print('Source:       ' + response.url)
    if ProductItem_fields:
        print('\n')
        print('ProductItem_fields')
        print(u'Name:      ', total_selector.xpath(ProductItem_fields['name']).extract())
        print(u'Price:     ', total_selector.xpath(ProductItem_fields['price']).re(r'\d+.\d+\S'))
        print(u'Currency:  ', total_selector.xpath(ProductItem_fields['currency']).re(r'\s.*'))
        print(u'Available: ', total_selector.xpath(ProductItem_fields['available']).extract())
        print(u'C.N.:      ', total_selector.xpath(ProductItem_fields['cn']))
        #print(u'C.N.:      ', total_selector.xpath(ProductItem_fields['cn']).re(r'\d+.\d')) #ParafarmaciaLastra

    if imgItem_fields:
        print('\n')
        print('imgItem')
        print(u'URL        ', total_selector.xpath(imgItem_fields['url']).extract()[0])

    # ImgDescriptionItem
    if descItem_fields:
        print('\n')
        print('descItem')
        print(u'Titulo     ', total_selector.xpath(descItem_fields['titulo']))
        print(u'Subtitulo  ', total_selector.xpath(descItem_fields['subtitulo']))
        print(u'Texto      ', total_selector.xpath(descItem_fields['texto']).extract())



