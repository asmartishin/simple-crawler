#!/usr/bin/env python3

import requests
import json
import argparse
from threading import Thread
from lib.utils import str2date, date2timestamp, get_username
from lib.logger import Logger
from lxml import html, etree
from pprint import pprint
from datetime import datetime, timedelta


class Crawler(object):
    def __init__(self, args, config):
        self.config = config
        self.main_page_selectors = config['selectors']['main_page']
        self.base_url = config['base_url']
        if args.daemon:
            self.data_update_interval = config['data_update_interval']
            self._spawn_cache_updater()

    def crawl(self):
        url = self.base_url + self.config['index_url']
        result = []

        min_timestamp = date2timestamp(datetime.now() - timedelta(1))
        continue_parsing = True

        while continue_parsing:
            result, url, continue_parsing = self.get_data_from_main_page(result, url, min_timestamp)

        pprint(result)

    # didn't use recursion, because of call stack overflow
    def get_data_from_main_page(self, result, url, min_timestamp):
        tree = etree.HTML(requests.get(url).text)
        for post in Crawler.dom_element_get_children(tree, self.main_page_selectors['post']):
            create_time = str2date(
                Crawler.dom_element_get_children(post, self.main_page_selectors['create_time'])[0].text)
            ctime = date2timestamp(create_time)

            if ctime < min_timestamp:
                return (result, url, False)

            post_title = Crawler.dom_element_get_children(post, self.main_page_selectors['post_title'])[0]
            post_author = Crawler.dom_element_get_children(post, self.main_page_selectors['post_title'])[0]

            result.append({
                'create_time': str(create_time),
                'ctime': ctime,
                'title': post_title.text,
                'href': post_title.get('href'),
                'author': get_username(post_author.get('href')).lower()
            })
        next_page = Crawler.dom_element_get_children(tree, self.main_page_selectors['next_page'])[0]
        url = self.base_url + next_page.get('href')
        return (result, url, True)

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
    with open('conf/crawler.conf.json') as conf_file:
        config = json.load(conf_file)
    logger = Logger('logs/crawler.log')
    crawler = Crawler(args, config)
    crawler.crawl()
