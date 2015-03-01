# -*- coding: utf-8 -*-

# Scrapy settings for my_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'FarmaTor'

SPIDER_MODULES = ['projects.spiders']
NEWSPIDER_MODULE = 'projects.spiders'

ITEM_PIPELINES = {
    'projects.pipelines.farmator': 300,
    }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Mocilla (+http://www.yourdomain.com)'

# Definicion de la base de datos mediante un diccionario
DATABASE = {'drivername': 'postgres',
            'host': 'localhost', # ToDo: Input your database host
            'port': '5432', # ToDo: Input your database port
            'username': '', # ToDo: Input your database username
            'password': '', # ToDo: Input your database password
            'database': ''}  # ToDo: Input your database name

