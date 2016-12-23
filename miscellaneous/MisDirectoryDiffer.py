#! -*- coding: utf-8 -*-

from miscellaneous.MisPlainFileDiffer import BasePlainFileDiffer
import os

def scandir(dir):
    for root, directory, filenames in os.walk(dir):
        for filename in filenames:
            if not filename.startswith('.'):
                yield os.path.join(root, filename)


class BaseDirectoryDiffer(object):
    """
    Compare two directory and differ by the same filename in two directory
    """
    def __init__(self, dir1, dir2):
        if not self.validate(dir1) or not self.validate(dir2):
            raise ValueError('is not a dir')

        self.dir1 = dir1
        self.dir2 = dir2
        self.files = self.list_files()

    def list_files(self, usegenerator=False):
        res = {}
        if usegenerator:
            res[self.dir1] = scandir(self.dir1)
            res[self.dir2] = scandir(self.dir2)
        else:
            res[self.dir1] = list(scandir(self.dir1))
            res[self.dir2] = list(scandir(self.dir2))
        return res

    def validate(self, dir):
        return os.path.isdir(dir)

    def _check_end_dir(self, dir):
        return dir.endswith(os.path.sep)

    def _remove_end_sep(self, dir):
        if self._check_end_dir(dir):
            return os.path.relpath(dir)
        return dir

    def _prefix(self, path):
        return os.path.dirname(path)

    def basename(self, dir):
        tmp = self._remove_end_sep(dir)
        prefix = self._prefix(tmp)
        return os.path.relpath(tmp, prefix)

    def _get_same_filename(self, l1, l2):
        _l1 = map(self.basename, l1)
        _l2 = map(self.basename, l2)
        return set(_l1) & set(_l2)

    def _fetch_by_same_filename(self, l1, l2):
        res = []
        for same in self._get_same_filename(l1, l2):
            _item = []
            for x in l1:
                if self.basename(x) == same:
                    _item.append(x)
            for x in l2:
                if self.basename(x) == same:
                    _item.append(x)
            res.append(_item)
        return res

    def differ(self):
        if len(self.files) != 2 and len(self.files) != 1:
            raise ValueError('Wrong data')
        data = list(self.files.values())
        for item in self._fetch_by_same_filename(data[0], data[1]):
            differ = BasePlainFileDiffer(self.basename(item[0]))
            print(differ.name)
            differ.clear_cache()
            differ.loadfile(item[0])
            differ.loadfile(item[1])
            d = differ.differ()
            for i in d.show_diff_content():
                print(i.info)

"""
if __name__ == "__main__":
    D = BaseDirectoryDiffer('/Users/kc-fu/test/test1', '/Users/kc-fu/test/test2/')
    D.differ()
"""