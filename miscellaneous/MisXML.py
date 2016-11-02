#! -*- coding: utf-8 -*-

"""
常见的XML编程接口有DOM和SAX，这两种接口处理XML文件的方式不同，当然使用场合也不同。
python有三种方法解析XML，SAX，DOM，以及ElementTree:
这里先介绍 SAX, 以及 DOM 的用法
具体文档可见: http://www.runoob.com/python3/python3-xml-processing.html
官方的 minidom 已封装足够好, 所以这边只是提下相关的method 用法等, 无须自己封装
"""


from xml.dom import minidom
from .MisExceptions import XMLParseError


class BaseDomXML(object):
    def __init__(self, xmlfile):
        self.xmlfile = xmlfile
        self.md = self._parser()
        self._tmp_parent = ''

    def _parser(self):
        try:
            md = minidom.parse(self.xmlfile)
        except:
            raise XMLParseError("Parse {} Error".format(self.xmlfile))
        else:
            return md

    def is_text_node(self, objectx):
        return objectx.nodeType == self.md.TEXT_NODE

    def is_element_node(self, objectx):
        return objectx.nodeType == self.md.ELEMENT_NODE

    def getelementsbytag(self, tag):
        """
        :param tag:
        :return: list of object
        """
        return self.md.getElementsByTagName(tag)

    def dig_elements(self, element, expand=False):

        if element.parentNode.nodeName != self._tmp_parent:
            self._tmp_parent = element.nodeName
            print(element.toprettyxml())

        for i in filter(self.is_element_node, element.childNodes):
            if not expand:
                print(i)
            else:
                self._tmp_parent = i.parentNode.nodeName
                self.dig_elements(i, expand=True)

    def digbytag(self, tag, expand=False):
        for el in self.md.getElementsByTagName(tag):
            if len(el.attributes.keys()) != 0:
                print(el.attributes.items())
            for i in filter(self.is_element_node, el.childNodes):
                if not expand:
                    print(i)
                else:
                    self.dig_elements(i, expand=True)

    # TODO, add more functions
