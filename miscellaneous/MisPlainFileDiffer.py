#! -*- coding: utf-8 -*-


import os
import mimetypes
from miscellaneous.MisExceptions import CacheError


class BasePlainFileDiffer(object):

    def __new__(cls, name):
        self = object.__new__(cls)
        self._cache = []
        return self

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    __str__ = __repr__

    def __call__(self):
        return self.__class__.__name__

    def loadfile(self, rawfile):
        if len(self._cache) == 2:
            raise CacheError("cache is full, call clear_cache!")
        elif self._check_file(rawfile):
            self._cache.append(rawfile)
        else:
            raise IOError('No {} file '.format(rawfile))
        return self

    def clear_cache(self):
        self._cache.clear()

    def _check_cache(self):
        return len(self._cache) == 2

    def _check_type(self, rawfile):
        return mimetypes.guess_type(rawfile)[0] == 'text/plain'

    def _check_file(self, rawfile):
        return os.path.isfile(rawfile) and self._check_type(rawfile)

    def differ(self):
        if self._check_cache():
            _first_file, _second_file = self._cache
            return Differ(_first_file, _second_file)


class Differ(object):

    def __init__(self, f1, f2):
        self.f1 = os.path.relpath(f1, os.path.dirname(f1))
        self.f2 = os.path.relpath(f2, os.path.dirname(f2))
        self.fp1 = self._try_open(f1)
        self.fp2 = self._try_open(f2)
        self.f1_info = os.stat(f1)
        self.f2_info = os.stat(f2)
        self._get_data()

    def __repr__(self):
        return self.__class__.__name__

    def __call__(self):
        return self.__class__.__name__

    def _try_open(self, file):
        try:
            _f = open(file, 'rb')
        except:
            raise IOError('Can not open {}'.format(file))
        return _f

    def __del__(self):
        self.fp1.close()
        self.fp2.close()

    def _get_data(self):
        self.fp1_data = self.fp1.readlines()
        self.fp2_data = self.fp2.readlines()

    def st_mode(self, verbose=False):
        _first_mode = self.f1_info.st_mode
        _second_mode = self.f2_info.st_mode
        _d = dict()
        _d[self.f1] = _first_mode
        _d[self.f2] = _second_mode
        if verbose:
            print(_d)
        return "Same" if _first_mode == _second_mode else "Not Same"

    def st_uid(self, verbose=False):
        _first_uid = self.f1_info.st_uid
        _second_uid = self.f2_info.st_uid
        _d = dict()
        _d[self.f1] = _first_uid
        _d[self.f2] = _second_uid
        if verbose:
            print(_d)
        return "Same" if _first_uid == _second_uid else "Not Same"

    def st_gid(self, verbose=False):
        _first_gid = self.f1_info.st_gid
        _second_gid = self.f2_info.st_gid
        _d = dict()
        _d[self.f1] = _first_gid
        _d[self.f2] = _second_gid
        if verbose:
            print(_d)
        return "Same" if _first_gid == _second_gid else "Not Same"

    def st_size(self, verbose=False):
        _first_size = self.f1_info.st_size
        _second_size = self.f2_info.st_size
        _d = dict()
        _d[self.f1] = _first_size
        _d[self.f2] = _second_size
        if verbose:
            print(_d)
        return "Same" if _first_size == _second_size else "Not Same"

    def st_atime(self, verbose=False):
        _first_atime = self.f1_info.st_atime
        _second_atime = self.f2_info.st_atime
        _d = dict()
        _d[self.f1] = _first_atime
        _d[self.f2] = _second_atime
        if verbose:
            print(_d)
        return "Same" if _first_atime == _second_atime else "Not Same"

    def st_mtime(self, verbose=False):
        _first_mtime = self.f1_info.st_mtime
        _second_mtime = self.f2_info.st_mtime
        _d = dict()
        _d[self.f1] = _first_mtime
        _d[self.f2] = _second_mtime
        if verbose:
            print(_d)
        return "Same" if _first_mtime == _second_mtime else "Not Same"

    def st_ctime(self, verbose=False):
        _first_ctime = self.f1_info.st_ctime
        _second_ctime = self.f2_info.st_ctime
        _d = dict()
        _d[self.f1] = _first_ctime
        _d[self.f2] = _second_ctime
        if verbose:
            print(_d)
        return "Same" if _first_ctime == _second_ctime else "Not Same"

    @property
    def is_same_content(self):
        return self.fp1_data == self.fp2_data

    def show_diff_content(self):
        if not self.is_same_content:
            for i in range(self.min_num):
                if self.fp1_data[i] == self.fp2_data[i]:
                    continue
                elif len(self.fp1_data[i].strip()) == 0 and len(self.fp2_data[i].strip()) != 0:
                    yield Adder(self.fp2_data[i], i)

                elif len(self.fp1_data[i].strip()) != 0 and len(self.fp2_data[i].strip()) == 0:
                    yield Deleter(self.fp1_data[i], i)

                elif self.fp1_data[i].strip() != self.fp2_data[i].strip():
                    yield Modify(self.fp1_data[i], self.fp2_data[i], i)

            if len(self.fp1_data) > len(self.fp2_data):
                other_num = len(self.fp1_data) - len(self.fp2_data)
                for i in range(other_num):
                    yield Deleter(self.fp1_data[self.min_num + i], self.min_num+i)

            if len(self.fp1_data) < len(self.fp2_data):
                other_num = len(self.fp2_data) - len(self.fp1_data)
                for i in range(other_num):
                    yield Adder(self.fp2_data[self.min_num + i], self.min_num+i)
        else:
            return None

    @property
    def min_num(self):
        num_1 = len(self.fp1_data)
        num_2 = len(self.fp2_data)
        if num_1 - num_2 >= 0:
            return num_2
        else:
            return num_1


class Line(object):
    def __init__(self,  lineno):
        self.lineno = lineno

    def __repr__(self):
        return "{0}-{1} Object".format(self.__class__.__name__, self.lineno)

    @property
    def content(self):
        return self.lineno


class AMD(object):
    def __init__(self, msg, number):
        self.msg = msg
        self.number = number

    @property
    def content(self):
        return self.msg

    @property
    def lineno(self):
        return self.number


class Adder(AMD):
    def __init__(self, msg, number):
        self.msg = msg
        self.number = number

        super(Adder, self).__init__(self.msg, self.number)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, Line(self.number))


class Deleter(AMD):
    def __init__(self, msg, number):
        self.msg = msg
        self.number = number
        super(Deleter, self).__init__(self.msg, self.number)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, Line(self.number))


class Modify(AMD):
    def __init__(self, msg1, msg2, number):
        self.msg1 = msg1
        self.msg2 = msg2
        self.number = number

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, Line(self.number))

    @property
    def before(self):
        return self.msg1

    @property
    def after(self):
        return self.msg2

    @property
    def content(self):
        return self.before, self.after

