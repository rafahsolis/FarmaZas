# -*- coding: utf-8 -*-

# Scrapy settings for my_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'FarmaZas'

SPIDER_MODULES = ['projects.spiders']
NEWSPIDER_MODULE = 'projects.spiders'

ITEM_PIPELINES = {
    'projects.pipelines.farmaTor': 300,
    }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mocilla (http://www.yourdomain.com)'
# Definicion de la base de datos mediante un diccionario

#@Warning: Database must be set
DATABASE = {'drivername': 'postgres',
            'host': 'DATABASE_HOST',
            'port': 'DATABASE_PORT',
            'username': 'DATABASE USERNAME',
            'password': 'DATABASE_PASWWORD',
            'database': 'DATABASE_NAME'}
