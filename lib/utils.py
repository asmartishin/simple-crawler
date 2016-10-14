import time
from datetime import datetime, timedelta
from dateutil import parser
from urllib.parse import urlparse
import re
import hashlib
import os
import json
import pymorphy2


class ConfigLoadError(Exception):
    pass


format_time = {
    'января': 'January',
    'февраля': 'February',
    'марта': 'March',
    'апреля': 'April',
    'мая': 'May',
    'июня': 'June',
    'июля': 'July',
    'августа': 'August',
    'сентября': 'September',
    'октября': 'October',
    'ноября': 'November',
    'декабря': 'December',
    ' в': '',
    'сегодня': datetime.now().strftime('%Y-%m-%d'),
    'вчера': (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
}

morph = pymorphy2.MorphAnalyzer()


def string_to_date(stime):
    format_time['сегодня'] = datetime.now().strftime('%Y-%m-%d')
    format_time['вчера'] = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    pattern = "|".join(re.escape(x) for x in format_time)
    return parser.parse(re.sub(pattern, lambda x: format_time.get(x.group(0).lower()), stime))


def date_to_timestamp(dtime):
    return int(time.mktime(dtime.timetuple()))


def get_username(url):
    return urlparse(url.rstrip('/')).path.rpartition('/')[2]


def string_to_hash(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()


def process_document_text(string):
    return re.sub(r'\s+', ' ', re.sub(r'[0-9]|[^\w\s]', '', string)).lower()


def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp)


def load_config(filename):
    if os.path.isfile(filename):
        try:
            with open(filename) as conf_file:
                return json.load(conf_file)
        except Exception as e:
            raise ConfigLoadError('Config is not a valid json')
    else:
        raise ConfigLoadError('Wrong config path "{}"'.format(filename))


def timestamp_today():
    return date_to_timestamp(datetime.now())


def timestamp_day_decrement(delta=1):
    return date_to_timestamp(datetime.now() - timedelta(delta))


def normalize_word(word):
    return morph.parse(word)[0].normal_form
