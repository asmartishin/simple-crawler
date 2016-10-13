#!/usr/bin/env python3

import requests
from lib.utils import string_to_date, date_to_timestamp, get_username, string_to_hash, process_document_text, \
    load_config, timestamp_day_decrement, timestamp_today
from lib.logger import Logger
from lib.mongo_connector import MongoConnector
from lxml import html, etree
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

    def update_database(self):
        url = self.base_url + self.config['index_url']
        min_timestamp = timestamp_day_decrement()
        self.download_and_index_posts(url, min_timestamp)

    def download_and_index_posts(self, url, min_timestamp):
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

                if not self.mongo.id_in_collection(document_id):
                    content = self.get_content_from_post(post_url)
                    inverted_index = self.create_inverted_index(content, document_id)
                    document = {
                        'create_time': str(create_time),
                        'ctime': ctime,
                        'post_title': post_title.text,
                        'document_url': post_url,
                        'document_id': document_id,
                        'post_author': get_username(post_author.get('href')).lower(),
                        'index': inverted_index
                    }
                    self.mongo.insert_document(document)
                    self.logger.info(
                        'Indexed document: "[{}] {}"'.format(document['create_time'], document['post_title']))
            next_page = Crawler.dom_element_get_children(tree, self.main_page_selectors['next_page'])[0]
            url = self.base_url + next_page.get('href')

    def get_content_from_post(self, url):
        html = requests.get(url)
        tree = etree.HTML(html.text)
        post_content = process_document_text("".join(tree.xpath('.//{}[contains(@class, "{}")]//text()'.format(
            self.post_page_selectors['content']['tag'], self.post_page_selectors['content']['selector'])))).strip()
        return post_content

    def create_inverted_index(self, content, document_id):
        inverted_index = {}
        forward_index = {index: word for index, word in enumerate(content.split())}
        for index, word in forward_index.items():
            word_normalized = self.morph.parse(word)[0].normal_form
            inverted_index.setdefault(word_normalized, []).append(index)
        return inverted_index

    @staticmethod
    def dom_element_get_children(root, selector_data):
        return root.xpath('.//{}[contains(@class, "{}")]'.format(selector_data['tag'], selector_data['selector']))


if __name__ == '__main__':
    crawler = Crawler(load_config('conf/crawler.conf.json'))
    crawler.update_database()
