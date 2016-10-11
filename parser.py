#!/usr/bin/env python3

import requests
import json
import argparse
from threading import Thread
from lib.data_converter import str2date, date2timestamp
from lib.logger import Logger
from lxml import html, etree


def parser(config):
    url = config['base'] + config['init']
    tree = etree.HTML(requests.get(url).text)
    post_selector = config['selectors']['posts_list']['post']
    for post in tree.xpath('//{tag}[contains(@class, "{selector}")]'.format(tag = post_selector['tag'], selector = post_selector['selector'])):
        ctime_selector = config['selectors']['posts_list']['ctime']
        print(str2date(post.xpath('.//{tag}[contains(@class, "{selector}")]/text()'.format(tag = ctime_selector['tag'], selector = ctime_selector['selector']))[0]))
#        print(post.xpath('.//div[@class = "{}"]'.format(config['selectors']['posts_list']['post_link']))[0].text)
#        print(date2timestamp(str2date(element.text)))


class DataParser(object):
    def __init__(self, args, config):
        self._download_data()
        if args.daemon:
            self.data_update_interval = config['data_update_interval']
            self._spawn_cache_updater()

    def _download_data(self):
        pass

    def _spawn_data_updater(self):
        self.log.info('Spawning cache updater ({}s)'.format(self.data_updater_interval))
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
    with open('conf/parser.conf.json') as conf_file:
            config = json.load(conf_file)
    logger = Logger('logs/parser.log')
    data_parser = DataParser(args, config)
    parser(config)
