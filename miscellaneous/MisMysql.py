#! -*- coding: utf-8 -*-
import mysql.connector as mc
from .MisExceptions import DBError


class BaseDB(object):
    def __init__(self, host, user, password, port=3306, charset='utf8', connect_timeout=5):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.charset = charset
        self.connect_timeout = connect_timeout
        try:
            self.conn = mc.connect(host=self.host, user=self.user, password=self.password, port=self.port,
                                   charset=self.charset, connect_timeout=self.connect_timeout)
        except mc.Error as e:
            raise DBError(e)
        else:
            self.cursor = self.conn.cursor()

    def commit_or_rollback(self, sqlcmd):
        try:
            self.cursor.execute(sqlcmd)
        except mc.Error as e:
            self.conn.rollback()
            raise DBError(e)
        else:
            self.conn.commit()

    # TODO: add more function to check the mysql status or some set functions
