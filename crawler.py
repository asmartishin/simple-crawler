#!/usr/bin/env python3

import requests
import json
import argparse
from threading import Thread
from lib.utils import string_to_date, date_to_timestamp, get_username, string_to_hash, remove_whitespaces, load_config
from lib.logger import Logger
from lxml import html, etree
from pprint import pprint
from datetime import datetime, timedelta
import pymorphy2


class Crawler(object):
    def __init__(self, args, config):
        self.config = config
        self.logger = Logger('logs/crawler.log').log
        self.main_page_selectors = config['selectors']['main_page']
        self.post_page_selectors = config['selectors']['post_page']
        self.base_url = config['base_url']
        self.data_from_main_page = []
        self.inverted_index = {}
        self.morph = pymorphy2.MorphAnalyzer()
        if args.daemon:
            self.data_update_interval = config['data_update_interval']
            self._spawn_data_updater()

    def get_data(self):
        url = self.base_url + self.config['index_url']
        min_timestamp = date_to_timestamp(datetime.now() - timedelta(1))
        data_from_posts = []
        self.data_from_main_page = self.get_data_from_main_page(url, min_timestamp)
        pprint(self.data_from_main_page)
        for post_data in self.data_from_main_page:
            document_id = post_data['document_id']
            content = self.get_data_from_post(post_data['document_url'])
            self._create_inverted_index(content, document_id, self.inverted_index)
        pprint(self.inverted_index)

    def get_data_from_main_page(self, url, min_timestamp):
        data_from_main_page = []
        data_from_posts = []
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

                data_from_main_page.append({
                    'create_time': str(create_time),
                    'ctime': ctime,
                    'post_title': post_title.text,
                    'document_url': post_url,
                    'document_id': document_id,
                    'post_author': get_username(post_author.get('href')).lower()
                })
            next_page = Crawler.dom_element_get_children(tree, self.main_page_selectors['next_page'])[0]
            url = self.base_url + next_page.get('href')
        return data_from_main_page

    def get_data_from_post(self, url):
        tree = etree.HTML(requests.get(url).text)
        post_content = remove_whitespaces("".join(tree.xpath('//{}[contains(@class, "{}")]/text()'.format(
            self.post_page_selectors['content']['tag'], self.post_page_selectors['content']['selector'])))).strip()
        return post_content

    def _create_inverted_index(self, content, document_id, inverted_index):
        forward_index = {index: word for index, word in enumerate(content.split())}
        for key, value in forward_index.items():
            value_normalized = self.morph.parse(value)[0].normal_form
            inverted_index.setdefault(value_normalized, {}).setdefault(document_id, []).append(key)

    @staticmethod
    def dom_element_get_children(root, selector_data):
        return root.xpath('.//{}[contains(@class, "{}")]'.format(selector_data['tag'], selector_data['selector']))

    def _spawn_data_updater(self):
        self.log.info('Spawning crwaler,  ({}s)'.format(self.data_updater_interval))
        self.cache_updater = Thread(
            target=self._update_cache,
            daemon=True
        )
        self.cache_updater.start()

    def _data_updater(self):
        while True:
            time.sleep(self.data_updater_interval)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script for parsing content from articles, calculates IDF')
    parser.add_argument('-d', '--daemon', action='store_true', help='Run script as daemon')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    config = load_config('conf/crawler.conf.json')
    crawler = Crawler(args, config)
    crawler.get_data()
