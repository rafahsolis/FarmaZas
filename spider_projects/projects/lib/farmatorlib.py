
from projects.models import db_connect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import Join, MapCompose
from scrapy.selector import Selector

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
        id=''
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