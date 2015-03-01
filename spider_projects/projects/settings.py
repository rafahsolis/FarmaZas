# -*- coding: utf-8 -*-

# Scrapy settings for my_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'FarmaciaFrias'

SPIDER_MODULES = ['projects.spiders']
NEWSPIDER_MODULE = 'projects.spiders'

ITEM_PIPELINES = {
    'projects.pipelines.FarmaciaFriasPipeline': 300,
    }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla (+http://www.yourdomain.com)'

DATABASE = {'drivername': 'postgres',
            'host': '', # ToDo: Input your database host
            'port': '', # ToDo: Input your database port
            'username': '', # ToDo: Input your database username
            'password': '', # ToDo: Input your database password
            'database': ''} # ToDo: Input your database name
