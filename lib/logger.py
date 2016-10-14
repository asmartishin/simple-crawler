import logging
import os


class Singleton(object):
    def __new__(cls, *args, **kwds):
        if not hasattr(cls, '__self__'):
            instance = object.__new__(cls)
            instance.init(*args, **kwds)
            setattr(cls, '__self__', instance)
        return getattr(cls, '__self__')

    def init(self, *args, **kwds):
        pass


class Logger(Singleton):
    def __init__(self, filename='debug.log'):
        folder = os.path.dirname(filename)
        if not os.path.exists(folder) and folder:
            os.makedirs(folder)
        self.log = logging.getLogger('main')
        if not len(self.log.handlers):
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
