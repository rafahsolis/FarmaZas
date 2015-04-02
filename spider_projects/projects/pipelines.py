# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy.orm import sessionmaker
from models import create_all_tables, CategoryModel, db_connect, ProductModel, SiteModel, ImgModel, DescriptionModel
from items import CategoryItem, ProductItem, SiteItem, DescriptionItem, ImgItem
from sqlalchemy import text


class farmaTor(object):
    """FarmaciaFrias pipeline for storing scraped items in the database"""
    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        """
        engine = db_connect()
        create_all_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save categorys in the database.

        This method is called for every item pipeline component.

        """

        session = self.Session()
        itemModel = False

        if type(item) == type(CategoryItem()):
            """ Si item es una categoria """
            if self.hashexist(session, item):
                """ Si existe y no ha cambiado no lo inserta"""
                self.printaction('La categoria ya existe', item) #Linea de debug
                session.close()
                return 'No se hicieron cambios'
            elif self.urlexist(session, item['url'], 'categorytable'):
                """ Si existe pero ha cambiado modifica la categoria"""
                self.updateitem(session, item)
                self.conection_add_commit(session, False, item)
                self.printaction('Se modifico la categoria')
            else:
                """ Si no existe lo inserta"""
                itemModel = CategoryModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo la categoria', item)

        elif type(item) == type(ProductItem()):
            """ Si item es un producto"""
            if self.hashexist(session, item):
                """ Si existe y no ha cambiado no lo inserta """
                self.printaction('El producto ya existe', item)
                session.close()
            elif self.urlexist(session, item['url'], 'productable'):
                """ Si existe pero ha cambiado modifica el registro """
                self.updateitem(session, item)
                self.conection_add_commit(session, False, item)
                self.printaction('Se modifico el producto', item)
            else:
                """ Si no existe lo inserta """
                itemModel = ProductModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo el producto', item)

        elif type(item) == type(SiteItem()):
            """ Si item es un site """
            if self.hashexist(session, item):
                """ Si existe y no ha cambiado no lo inserta """
                self.printaction('Site ya existe', item)
                session.close()
            elif self.urlexist(session, item['url'], 'sitetable'):
                """ Si existe pero ha cambiado modifica el registro """
                self.updateitem(session, item)
                self.conection_add_commit(session, False, item)
                self.printaction('Se modifico el site', item)
            else:
                """ Si no existe lo inserta """
                itemModel = SiteModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo el site', item)

        elif type(item) == type(DescriptionItem()):
            """ Si item es un descripcion """
            if self.hashexist(session, item):
                """ Si existe y no ha cambiado no lo inserta """
                self.printaction('La descripcion ya existe', item)
                session.close()
            elif self.urlexist(session, item['producturl'], 'desctable'):
                """ Si existe pero ha cambiado modifica el registro """
                self.updateitem(session, item)
                self.conection_add_commit(session, False, item)
                self.printaction('Se modifico la descripcion', item)
            else:
                """ Si no existe lo inserta """
                itemModel = DescriptionModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo la descripcion', item)

        elif type(item) == type(ImgItem()):
            """ Si item es una imagen"""
            if self.hashexist(session, item):
                """ Si existe y no ha cambiado no lo inserta """
                self.printaction('La imagen ya existe', item)
                session.close()
            elif self.urlexist(session, item['producturl'], 'imgtable'):
                """ Si existe pero ha cambiado modifica el registro """
                self.updateitem(session, item)
                self.conection_add_commit(session, False, item)
                self.printaction('Se modifico la imagen', item)
            else:
                """ Si no existe lo inserta """
                itemModel = ImgModel(**item)
                self.conection_add_commit(session, itemModel, item)
                self.printaction('Se introdujo la imagen', item)
    def conection_add_commit(self, session, itemModel, item): 
        try:
            if itemModel:
                session.add(itemModel)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        #ToDo comprobar si este retrun devuelve none
        if itemModel and item:
            return item

    def hashexist(self, session, item):
        # Comprueba si existe un hash
        #@Warning: Acordarse de cambiar si se cambian los nombres de las tablas

        #ToDo: Ojo, se estan haciendo pops, QUE ALGUIEN QUITE ESTA CHAPUZA ;-) item['*'] = item['*].pop(), item['id_category'] = item['id_category'].pop()

        if type(item) == type(CategoryItem()):
            item['id_site'] = item['id_site'].pop()
            tabla = 'categorytable'
        elif type(item) == type(ProductItem()):
            item['id_site'] = item['id_site'].pop()
            item['id_category'] = item['id_category'].pop()
            tabla = 'productable'
        elif type(item) == type(DescriptionItem()):
            item['id_product'] = item['id_product'].pop()
            tabla = 'desctable'
        elif type(item) == type(ImgItem()):
            item['id_site'] = item['id_site'].pop()
            item['id_product'] = item['id_product'].pop()
            tabla = 'imgtable'
        elif type(item) == type(SiteItem()):
            tabla = 'sitetable'
        else:
            self.printaction('hashexists() en pipelines.py no reconocio el item', type(item))
            tabla = False

        if tabla:
            hashlist = session.execute(
                text("SELECT * FROM " + tabla + " WHERE hash=:hashtocheck"),
                {"hashtocheck": item['hash']})

        else:
            hashlist = None

        if hashlist.rowcount!= 0:
            return True
        else:
            return False
    #ToDo: Actualizar para el resto de tablas
    #ToDo: Cambiar campo relacion producto con img desc etc utilizar id producto
    def urlexist(self, session, urltocheck, tabla=None):
        #Comprueba si existe la url de un producto en la base de datos
        #Falta añadir caso de que URL no sea buena
        if tabla == 'productable':
            urllist = session.execute(
            text("SELECT * FROM productable WHERE url=:urlcheck"),
            {"urlcheck": urltocheck}
            )
        elif tabla == 'categorytable':
            urllist = session.execute(
            text("SELECT * FROM categorytable WHERE url=:urlcheck"),
            {"urlcheck": urltocheck}
            )
        elif tabla == 'desctable':
            urllist = session.execute(
            text("SELECT * FROM desctable WHERE producturl=:urlcheck"),
            {"urlcheck": urltocheck}
            )
        elif tabla == 'imgtable':
            urllist = session.execute(
            text("SELECT * FROM imgtable WHERE producturl=:urlcheck"),
            {"urlcheck": urltocheck}
            )
        elif tabla == 'sitetable':
            urllist = session.execute(
            text("SELECT * FROM sitetable WHERE url=:urlcheck"),
            {"urlcheck": urltocheck}
            )
        else:
            self.printaction(actionstring='No se identifico la tabla donde buscar url en urlexists')


        if urllist.rowcount != 0:
            return True
        else:
            return False
    #
    def printaction(self, actionstring, item=None):
        print('<--  PIPELINE DEBUG  --> ', actionstring)
        if item:
            print('hash: ', item['hash'])


    def updateitem(self, session, item):
        #Actualiza un item existente
        if type(item) == type(ProductItem()):
            updateobj = session.execute(
                text("UPDATE  productable SET "
                    "name=:newname, "
                    "price=:newprice, "
                    "currency=:newcurrency, "
                    "available=:newavailable, "
                    "cn=:newcn, "
                    "hash=:newhash "
                    "WHERE url=:searchurl"),
                {"newname": item['name'],
                 "newprice": item['price'],
                 "newcurrency": item['currency'],
                 "newavailable": item['available'],
                 "newcn": item['cn'],
                 "newhash": item['hash'],
                 "searchurl": item['url']}
            )
            session.commit()
        if type(item) == type(CategoryItem()):
            updateobj = session.execute(
                text("UPDATE  categorytable SET "
                    "name=:newname, "
                    "description=:newdescription, "
                    "parent=:newparent, "
                    "hash=:newhash "
                    "WHERE url=:searchurl"),
                {"newname": item['name'],
                 "newdescription": item['description'],
                 "newparent": item['parent'],
                 "newhash": item['hash'],
                 "searchurl": item['url']}
            )
            session.commit()
        elif type(item) == type(DescriptionItem()):
            updateobj = session.execute(
                text("UPDATE  desctable SET "
                     "titulo=:newtitulo, "
                     "texto=:newtexto, "
                     "desc_date=:newdesc_date, "
                     "desc_type=:newdesc_type, "
                     "hash=:newhash "
                     "WHERE producturl=:searchproducturl"),
                {"newtitulo": item['titulo'],
                 "newtexto": item['texto'],
                 "newdesc_date": item['desc_date'],
                 "newdesc_type": item['desc_type'],
                 "newhash": item['hash'],
                 "searchproducturl": item['producturl']}
            )
            session.commit()
        elif type(item) == type(ImgItem()):
            updateobj = session.execute(
                text("UPDATE  imgtable SET "
                     "id_site=:newid_site, "
                     "source_url=:newsourceurl, "
                     "img_type=:newimgtype, "
                     "hash=:newhash "
                     "WHERE producturl=:url"),
                {"newid_site": item['id_site'],
                 "newsource_url": item['source_url'],
                 "newimg_type": item['img_type'],
                 "newhash": item['hash'], "producturl": item['producturl']}
            )
            session.commit()
        elif type(item) == type(SiteItem()):
            updateobj = session.execute(
                text("UPDATE  sitetable SET "
                     "sp1_status=:newsp1status, "
                     "sp2_status=:newsp2status, "
                     "last_update=:newlastupdate, "
                     "error_log=:newerrorlog, "
                     "hash=:newhash "
                     "WHERE id_site=:searchid_site"),
                {"newname": item['name'],
                 "newprice": item['price'],
                 "newcurrency": item['currency'],
                 "newavailable": item['available'],
                 "newhash": item['hash'],
                 "searchid_site": item['id_site']}
            )
            session.commit()


