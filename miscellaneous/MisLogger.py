#! -*- coding: utf-8 -*-

import os
import logging

class Singleton(type):

    def __new__(cls, *args, **kwargs):
        _cls = super(Singleton, cls).__new__(cls, *args, **kwargs)
        _cls._instance = None
        return _cls

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            inst = cls.__new__(cls, *args, **kwargs)
            cls._instance = inst
        return cls._instance



class BaseLogger(metaclass=Singleton):
    LOGGER_DIR = "logs"

    def __init__(self, name):
        self.name = name
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        self.file_name = os.path.join(os.path.dirname(__file__), BaseLogger.LOGGER_DIR, '%s.log' % self.name)
        handler = logging.FileHandler(self.file_name)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d In %(filename)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    def get(self):
        return self.logger

"""
    if defined the your logger class as mention, then you can use it anywhere to log something.
    etc:
    import BaseLogger
    class YourCustomClass(object):
        def __init__(self):
            self.logger = BaseLogger(self.__class__.__name__).get()

        def do_somethings(self):
            self.logger.info('BALA BALA')

        def do_otherthings(self):
            self.logger.debug('BALA BALA')
"""
