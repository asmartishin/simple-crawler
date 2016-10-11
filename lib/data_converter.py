import time
from datetime import datetime, timedelta
from dateutil import parser
import re

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

def str2date(stime):
    format_time['сегодня'] = datetime.now().strftime('%Y-%m-%d')
    format_time['вчера'] = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    pattern = "|".join(re.escape(x) for x in format_time)
    return parser.parse(re.sub(pattern, lambda x: format_time.get(x.group(0).lower()), stime))


def date2timestamp(dtime):
    return int(time.mktime(dtime.timetuple()))
