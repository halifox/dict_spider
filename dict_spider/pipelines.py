# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from pymongo import ASCENDING


class DictSpiderPipeline:
    def __init__(self):
        self.client = None
        self.db = None

    def open_spider(self, spider):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')
        self.db = self.client['dict_spider']
        self.db['sogou'].create_index([('type', ASCENDING), ('id', ASCENDING)], unique=True)
        self.db['baidu'].create_index([('type', ASCENDING), ('id', ASCENDING)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        source = item['source']
        try:
            self.db[source].insert_one(item)
        except:
            pass
        return item
