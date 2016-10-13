from pymongo import MongoClient


class IndexInsertError(Exception):
    pass


class MongoConnector(object):
    def __init__(self, config):
        self.config = config
        self.db = MongoClient(config['host'], config['port'])[config['db']]
        self.data = self.db[config['data']]

    def insert_document(self, data):
        if not data['index']:
            raise IndexInsertError('No document index')
        doc = {
            '_id': data['document_id'],
            'ctime': data['ctime'],
            'url': data['document_url'],
            'author': data['post_author'],
            'title': data['post_title'],
            'index': data['index']
        }
        self.data.insert(doc)

    def id_in_collection(self, key):
        return bool(self.data.find_one({'_id': key}))

    def filter_users_by_time(self, start_timestamp, end_timestamp):
        result = self.data.find(
            {
                'ctime':
                    {
                        '$gt': start_timestamp,
                        '$lt': end_timestamp
                    }
            }
        ).distinct('author')
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

    def filter_index_by_documents(self, start_timestamp, end_timestamp):
        result = self.data.find(
            {
                'ctime': {
                    '$gt': start_timestamp,
                    '$lt': end_timestamp
                }
            }
        ).distinct('index')
        return result
