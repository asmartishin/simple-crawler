from pymongo import MongoClient


class MongoConnector(object):
    def __init__(self, config):
        self.config = config
        self.db = MongoClient(config['host'], config['port'])[config['db']]
        self.data = self.db[config['data']]
        self.index = self.db[config['index']]

    def insert_document(self, data, collection):
        if collection == self.config['data']:
            doc = {
                '_id': data['document_id'],
                'ctime': data['ctime'],
                'url': data['document_url'],
                'author': data['post_author'],
                'title': data['post_title']
            }
            self.data.insert(doc)
        elif collection == self.config['index']:
            for word, word_occurances in data.items():
                if not self.key_in_collection(word, self.config['index']):
                    doc = {
                        '_id': word,
                        'index': word_occurances
                    }
                    self.index.insert(doc)
                else:
                    for document_hash, document_occurances in word_occurances.items():
                        self.index.update({'_id': word}, {'$set': {'value.' + document_hash: document_occurances}})

    def key_in_collection(self, key, collection):
        return bool(self.db[self.config[collection]].find_one({'_id': key}))

    def filter_users_by_time(self, start_timestamp, end_timestamp):
        result = self.data.find(
            {
                'ctime':
                    {
                        '$gt': start_timestamp,
                        '$lt': end_timestamp
                    }
            },
            {
                'author': 1,
                '_id': 0
            }
        )
        return list(result)

    def filter_posts_by_user(self, user, start_timestamp, end_timestamp):
        result = self.data.find(
            {
                '$and': [
                    {
                        'ctime': {
                            '$gt': start_timestamp,
                            '$lt': end_timestamp
                        }
                    },
                    {
                        'author': user
                    }
                ]
            },
            {
                'title': 1,
                'ctime': 1,
                '_id': 0
            }
        )
        return list(result)
