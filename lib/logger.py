import logging
import os


class Logger(object):
    def __init__(self, filename='debug.log'):
        folder = os.path.dirname(filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.log = logging.getLogger('main')
        handler = logging.FileHandler(filename)
        console = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%d/%m/%Y:%H:%M:%S')
        )
        console.setFormatter(logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%d/%m/%Y:%H:%M:%S')
        )
        self.log.addHandler(handler)
        self.log.addHandler(console)
        self.log.setLevel(logging.DEBUG)
