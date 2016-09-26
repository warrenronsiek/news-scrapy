# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from bs4 import BeautifulSoup


class JezebelCleaner(object):
    def process_item(self, item, spider):
        try:
            item['author'] = BeautifulSoup(item['author'][0], 'lxml').text
        except AttributeError, err:
            print item['url']
            print err
        try:
            item['date'] = BeautifulSoup(item['date'][0], 'lxml').time['datetime']
        except AttributeError, err:
            print item['url']
            print err
        try:
            item['title'] = BeautifulSoup(item['title'][0], 'lxml').text
        except AttributeError, err:
            print item['url']
            print err
        try:
            item['url'] = item['url'][0]
        except:
            print item
        try:
            item['text'] = item['text'][0]
        except:
            print item
        return item


class MongoPipeline(object):

    collection_name = 'jezebel'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = 'mongodb://localhost:27017/'
        self.mongo_db = 'news'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))
        return item
