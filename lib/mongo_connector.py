from pymongo import MongoClient


class MongoConnector(object):
    def __init__(self, host='localhost', port='27017'):
        self.db = MongoClient().test
        self.articles = self.db.articles
