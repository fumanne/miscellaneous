#! -*- coding: utf-8 -*-

import os
import socket
import struct
import re
import sqlite3
from collections import namedtuple
from .MisExceptions import FileNotFoundError
from .MisExceptions import IP2CountryStatusError
from urllib.request import urlopen


class IP2Country(object):
    IP_REGEX = "^(([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).){3}([1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

    def __init__(self):
        self.DBSearcher = None
        self.FileSearcher = None

    def set(self, method="db"):
        """
        :param method: choice  db or file
        :return: FileSearcher Object or DBSearcher At the Same object just only One object exist
        """

        if method == 'file':
            self.FileSearcher = FileSearcher()
            self.DBSearcher = None
        elif method == 'db':
            self.DBSearcher = DBSearcher()
            self.FileSearcher = None

    @property
    def method(self):
        if self.FileSearcher:
            return self.FileSearcher
        if self.DBSearcher:
            return self.DBSearcher

    @property
    def status(self):
        return self.FileSearcher is not None or self.DBSearcher is not None

    @staticmethod
    def filter_wrong_ip(ip):
        ip_regex = re.compile(IP2Country.IP_REGEX)
        return re.match(ip_regex, ip) is not None

    def search(self, *args):
        """
        :param args: ip args, if ip is wrong formatter, it will be ignore it.
        :return: dict key ==> ip value ==> country
        """
        if not self.status:
            raise IP2CountryStatusError("is not set")
        result = dict()
        for i in filter(self.filter_wrong_ip, args):
            if self.FileSearcher:
                result[i] = self.FileSearcher.search(i)

            if self.DBSearcher:
                result[i] = self.DBSearcher.search(i)
        return result

    @classmethod
    def update(cls):
        return Updater().update()


class Util(object):
    @classmethod
    def ip2long(cls, ip):
        return struct.unpack("!L", socket.inet_aton(ip))[0]

    @classmethod
    def long2ip(cls, long):
        return socket.inet_ntoa(struct.pack("!L", long))


class IPv4Range(namedtuple('IPv4Range', ['start_long_ip', 'end_long_ip', 'country'])):
    """
        传入起始ip, 结束ip, 以及国家码, 实例创建的时候 通过__new__ 将 起始ip 和 结束ip 转变为 long ip 型
        即 内置属性名称就是为 start_long_ip, end_long_ip, country
        官方文档 对namedtuple 有很好的说明, 详见:
        https://docs.python.org/3/library/collections.html#collections.namedtuple
    """
    def __new__(cls, start_ip, end_ip, country):
        start = Util.ip2long(start_ip)
        end = Util.ip2long(end_ip)
        return tuple.__new__(cls, (start, end, country))

    @property
    def start(self):
        return Util.long2ip(self.start_long_ip)

    @property
    def end(self):
        return Util.long2ip(self.end_long_ip)

    def contains(self, target):
        target_long = Util.ip2long(target)
        return self.start_long_ip <= target_long <= self.end_long_ip


class Resource(object):
    def __init__(self):
        _filename = 'resource/ip.tsv'
        _abs_filename = os.path.join(os.path.dirname(__file__), '..', _filename)
        if not os.path.exists(_abs_filename):
            raise FileNotFoundError("Not Found {}, use Update to Download".format(_abs_filename))
        self._filename = _abs_filename

    @property
    def filename(self):
        return self._filename


class DBSearcher(Resource):
    def __init__(self):
        super(DBSearcher, self).__init__()
        self.con = sqlite3.connect(":memory:")
        self.con.isolation_level = None
        self._init_db()

    def __call__(self):
        return self.con

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__

    def _init_db(self):
        cur = self.con.cursor()
        init_sql_1 = ''' CREATE TABLE ip2country (start BIGINT NOT NULL, \
        end BIGINT NOT NULL, country CHARACTER(10) NOT NULL);'''
        init_sql_2 = "CREATE INDEX start_end_index ON ip2country (start,end);"
        cur.execute(init_sql_1)
        cur.execute(init_sql_2)
        with open(self._filename) as fp:
            for record in fp:
                record = record.strip().split()
                insert_sql = 'insert into ip2country(start, end, country) values({0:d}, {1:d}, "{2:s}")'.format(Util.ip2long(record[0]),
                                                                                                        Util.ip2long(record[1]),
                                                                                                        record[2])
                cur.execute(insert_sql)
            self.con.commit()
        cur.close()

    def search(self, target):
        cur = self.con.cursor()
        cur.execute("select country from ip2country where start <= {0:d} and end >= {0:d}".format(Util.ip2long(target)))
        res = cur.fetchone()
        if res is not None:
            res = res[0]
        cur.close()
        return res

    def __del__(self):
        self.con.close()


class FileSearcher(Resource):
    def __init__(self):
        super(FileSearcher, self).__init__()
        self._ip_range = self._init_data()

    def __call__(self):
        return self._ip_range

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__

    def _init_data(self):
        ip_range = []
        with open(self._filename) as fp:
            for record in fp:
                record = record.strip()
                record = record.split()
                ip_range.append(IPv4Range(*record))
        return ip_range

    def search(self, target):
        for i in self._ip_range:
            if i.contains(target):
                return i.country


class Updater(Resource):
    def __init__(self):
        super(Updater, self).__init__()

    def update(self):
        """
        update the resouce/ip.tsv from internet
        :return: None
        """
        total_record_count = 0
        with open(self._filename, 'w') as fp:
            for rir in allrepos():
                print("Read from {}".format(rir.name))
                rir_records = rir.download()
                for i in rir_records:
                    fp.write('{:s}\t{:s}\t{:s}\n'.format(*i))
                    total_record_count += len(rir_records)
        print('Total Update record is {}'.format(total_record_count))


def allrepos():
    return [
        AFRINIC(),
        APNIC(),
        LACNIC(),
        RIPENICC(),
        ARIN()
    ]


class RegionInternetRepo(object):

    @staticmethod
    def is_ipv4(record):
        # TODO, whether can be used with abstract method by abc class?
        return NotImplementedError()

    @staticmethod
    def skip_record(record):
        """
        :param record: 4 status: available/ allocated / assigned / reserved
        only allocated and  assigned can find the country
        :return: bool
        """
        words = record.split('|')
        return words[6] != 'allocated' and words[6] != 'assigned'

    @staticmethod
    def parse_ipv4(record):
        words = record.split('|')
        country = words[1]
        start_ip = words[3]
        length_ip = int(words[4])
        end_ip = Util.long2ip(Util.ip2long(start_ip) + length_ip - 1)

        return start_ip, end_ip, country

    @property
    def download_url(self):
        return NotImplementedError()

    def download(self):
        result = []
        with urlopen(self.download_url) as fp:
            for record in fp:
                record = record.decode('utf-8').strip()
                if self.is_ipv4(record) and not self.skip_record(record):
                    result.append(self.parse_ipv4(record))
        return result


class StandardFileFormatRegionInternetRepo(RegionInternetRepo):

    @staticmethod
    def is_ipv4(record):
        words = record.split('|')
        if len(words) == 7 and words[2] == 'ipv4':
            return True
        else:
            return False


class ExtendedFileFormatRegionInternetRepo(RegionInternetRepo):
    @staticmethod
    def is_ipv4(record):
        words = record.split('|')
        if len(words) == 8 and words[2] == 'ipv4':
            return True
        else:
            return False


class AFRINIC(StandardFileFormatRegionInternetRepo):
    @property
    def name(self):
        return 'Afrinic'

    @property
    def download_url(self):
        return 'http://ftp.apnic.net/stats/afrinic/delegated-afrinic-latest'


class APNIC(StandardFileFormatRegionInternetRepo):
    @property
    def name(self):
        return 'Apnic'

    @property
    def download_url(self):
        return 'http://ftp.apnic.net/stats/apnic/delegated-apnic-latest'


class LACNIC(StandardFileFormatRegionInternetRepo):
    @property
    def name(self):
        return 'Lacnic'

    @property
    def download_url(self):
        return 'http://ftp.apnic.net/stats/lacnic/delegated-lacnic-latest'


class RIPENICC(StandardFileFormatRegionInternetRepo):
    @property
    def name(self):
        return 'Ripenicc'

    @property
    def download_url(self):
        return 'http://ftp.apnic.net/stats/ripe-ncc/delegated-ripencc-latest'


class ARIN(ExtendedFileFormatRegionInternetRepo):
    @property
    def name(self):
        return "Arin"

    @property
    def download_url(self):
        return 'http://ftp.apnic.net/stats/arin/delegated-arin-extended-latest'

