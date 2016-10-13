#!/usr/bin/env python3

import requests
from lib.utils import string_to_date, date_to_timestamp, get_username, string_to_hash, remove_whitespaces, load_config
from lib.logger import Logger
from lib.mongo_connector import MongoConnector
from lxml import html, etree
from datetime import datetime, timedelta
import pymorphy2


class Crawler(object):
    def __init__(self, config):
        self.config = config
        self.logger = Logger('logs/debug.log').log
        self.mongo = MongoConnector(load_config('conf/db.conf.json'))
        self.main_page_selectors = config['selectors']['main_page']
        self.post_page_selectors = config['selectors']['post_page']
        self.base_url = config['base_url']
        self.morph = pymorphy2.MorphAnalyzer()

    def update_data(self):
        self.logger.info('asd')
        url = self.base_url + self.config['index_url']
        min_timestamp = date_to_timestamp(datetime.now() - timedelta(1))
        new_documents_from_main_page = self.get_documents_from_main_page(url, min_timestamp)
        for document in new_documents_from_main_page:
            document_id = document['document_id']
            content = self.get_content_from_post(document['document_url'])
            self.update_inverted_index(content, document_id)
        self.logger.info('Index updated')

    def get_documents_from_main_page(self, url, min_timestamp):
        new_documents_from_main_page = []
        continue_parsing = True
        while continue_parsing:
            tree = etree.HTML(requests.get(url).text)
            for post in Crawler.dom_element_get_children(tree, self.main_page_selectors['post']):
                create_time = string_to_date(
                    Crawler.dom_element_get_children(post, self.main_page_selectors['create_time'])[0].text)
                ctime = date_to_timestamp(create_time)

                if ctime < min_timestamp:
                    continue_parsing = False
                    break

                post_title = Crawler.dom_element_get_children(post, self.main_page_selectors['post_title'])[0]
                post_author = Crawler.dom_element_get_children(post, self.main_page_selectors['post_author'])[0]
                post_url = post_title.get('href')
                document_id = string_to_hash(post_title.get('href'))

                if not self.mongo.id_in_collection(document_id, 'data'):
                    document = {
                        'create_time': str(create_time),
                        'ctime': ctime,
                        'post_title': post_title.text,
                        'document_url': post_url,
                        'document_id': document_id,
                        'post_author': get_username(post_author.get('href')).lower()
                    }
                    self.mongo.insert_document(document, 'data')
                    new_documents_from_main_page.append(document)

                    self.logger.info('Inserted document: "{}"'.format(document))
            next_page = Crawler.dom_element_get_children(tree, self.main_page_selectors['next_page'])[0]
            url = self.base_url + next_page.get('href')
        return new_documents_from_main_page

    def get_content_from_post(self, url):
        tree = etree.HTML(requests.get(url).text)
        post_content = remove_whitespaces("".join(tree.xpath('//{}[contains(@class, "{}")]/text()'.format(
            self.post_page_selectors['content']['tag'], self.post_page_selectors['content']['selector'])))).strip()
        return post_content

    def update_inverted_index(self, content, document_id):
        inverted_index = {}
        forward_index = {index: word for index, word in enumerate(content.split())}
        for key, value in forward_index.items():
            value_normalized = self.morph.parse(value)[0].normal_form
            inverted_index.setdefault(value_normalized, {}).setdefault(document_id, []).append(key)
        self.mongo.insert_document(inverted_index, 'index')

    @staticmethod
    def dom_element_get_children(root, selector_data):
        return root.xpath('.//{}[contains(@class, "{}")]'.format(selector_data['tag'], selector_data['selector']))

if __name__ == '__main__':
    crawler = Crawler(load_config('conf/crawler.conf.json'))
    crawler.update_data()
