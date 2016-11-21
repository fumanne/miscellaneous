#! -*- coding: utf-8 -*-
import mysql.connector as mc
from miscellaneous.MisExceptions import DBError


class BaseDB(object):
    def __init__(self, host, user, password, port=3306, charset='utf8', connect_timeout=5):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.charset = charset
        self.connect_timeout = connect_timeout

        self.conn = None
        self.cur = None
        self.is_connected = False
        self.is_cur_connected = False



    def __repr__(self):
        return "{0}.connection".format(self.__class__.__name__)


    def connect(self):
        if not self.is_connected:
            try:
                _conn = mc.connect(host=self.host, user=self.user, password=self.password, port=self.port,
                                   charset=self.charset, connect_timeout=self.connect_timeout)
            except mc.Error as e:
                raise DBError(e)
            else:
                self.conn = _conn
                self.is_connected = True
                return self.conn

    def cursor(self, **kwargs):
        all_keys = ('buffered', 'raw', 'prepared', 'dictionary', 'named_tuple')
        for k in kwargs.keys():
            if k not in all_keys:
                raise KeyError("{} is not support".format(k))

        try:
            self.cur = self.conn.curosr(**kwargs)
        except:
            raise DBError()
        self.is_cur_connected = True
        return self.cur

    def commit_or_rollback(self, sqlcmd):
        if not self.is_cur_connected:
            raise DBError('curosr is not connected')

        try:
            self.cur.execute(sqlcmd)
        except mc.Error as e:
            self.conn.rollback()
            raise DBError(e)
        else:
            self.conn.commit()


    # TODO: Meaningless  will be deleted in future

    def __del__(self):
        self.conn.close()