#! -*- coding: utf-8 -*-
# 常见的excel一些用法整理

import xlrd
import xlwt
import os
import functools

class MisExcelReader(object):
    def __init__(self, excelfile):
        self.excel_reader = xlrd.open_workbook(excelfile)
        self.filename = self._trans(excelfile)

    def _trans(self, file):
        return os.path.relpath(os.path.abspath(file), os.path.dirname(file))

    def __repr__(self):
        return "{0}-<{1}>".format(self.__class__.__name__, self.filename)

    @property
    def get_sheets(self):
        """
        Get the list of sheet object
        :return: list
        """
        return self.excel_reader.sheets()

    @property
    def get_sheetsname(self):
        """
        Get the list of sheet name
        :return: list
        """
        return self.excel_reader.sheet_names()

    def get_sheet_by_name(self, name):
        """
        name : the name of sheet, from get_sheetsname function you will see all names
        :param name: sheet object
        :return:
        """
        return self.excel_reader.sheet_by_name(name)

    def get_sheet_by_index(self, index):
        """
        :param index: from list of sheets index
        :return: sheet object
        """
        return self.excel_reader.sheet_by_index(index)



class Dump(object):
    def dump(self):
        return self.dump()


class MisSheetReader(Dump):
    def __init__(self, sheet_obj):
        """
        :param sheet_obj:  is the sheet object, get from class::MisExcelReader.get_sheet_by_name or get_sheet_by_index
        :return:
        """
        self.sheet = sheet_obj
        self.ncols = self.sheet.ncols
        self.nrows = self.sheet.nrows
        self.name  = self.sheet.name

    def row(self, rowx=0):
        """
        :param rowx: int type
        :return: the list of cell object
        """
        if rowx <= self.nrows:
            return self.sheet.row(rowx)
        else:
            raise IndexError('Out of row range')

    def col(self, colx=0):
        """
        :param colx:  int type
        :return: list of cell type
        """
        if colx <= self.ncols:
            return self.sheet.col(colx)
        else:
            raise IndexError('Out of column range')

    def row_values(self, rowx, start_cols=0, end_colx=None):
        if rowx > self.nrows:
            raise IndexError('Out of row range')
        if start_cols > self.ncols or end_colx > self.ncols:
            raise IndexError('Out of range')
        if not end_colx:
            end_colx=self.ncols
        return self.sheet.row_values(rowx, start_cols, end_colx)

    def col_values(self, colx, start_rows=0, end_rows=None):
        if colx > self.ncols:
            raise IndexError('Out of  column range')
        if start_rows > self.nrows or end_rows > self.nrows:
            raise IndexError('Out of range')
        if not end_rows:
            end_rows = self.nrows
        return self.sheet.col_values(colx, start_rows, end_rows)

    def cell(self, rowx=0, colx=0):
        if rowx <= self.nrows and colx <= self.ncols:
            return self.sheet.cell(rowx, colx)
        else:
            raise IndexError('Out of range')


class MisExcelWriter(object):
    def __init__(self):
        self.wt = xlwt.Workbook(encoding='utf-8')
        self.sheets = []
        self.name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


    def add_sheet(self, sheet_name):
        """
        :param sheet_name:
        :return:  the sheet object
        """
        _sh = self.wt.add_sheet(sheet_name)
        self.sheets.append(_sh)
        return _sh

    def save(self, filename=None):
        if filename is None:
            filename = self.name
        return self.wt.save(filename)

class MisSheetWriter(object):
    def __init__(self, sheet_obj):
        self.sh = sheet_obj

    @property
    def name(self):
       return self.sh.name

    def row(self, rowx):
        return self.sh.row(rowx)

    def cols(self, colsx):
        return self.sh.col(colsx)

    def cell(self, rowx, colsx):
        return MisCellWriter(self,rowx, colsx)


class MisCellWriter(object):
    def __init__(self, cls, rowx, colsx):
        self.cls = cls
        self.rowx = rowx
        self.colsx = colsx

    def __repr__(self):
        return "{0}:<({1},{2})>".format(self.__class__.__name__, self.rowx, self.colsx)

    def writer(self, data):
        return self.cls.row(self.rowx).write(self.colsx, data)