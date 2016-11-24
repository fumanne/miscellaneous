#! -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
from urllib import request
import os
import re
from miscellaneous.MisExceptions import DouBanNotLoginError, DouBanCrawlNotCallError


class DouBanAuth(object):
    INDEX_URL = REDIR = 'https://www.douban.com'
    LOGIN_URL = 'https://accounts.douban.com/login'
    LOGIN_FLAG = '登录'

    def __init__(self, url=None):
        self.url = url if url else self.LOGIN_URL
        self.islogin = False
        self.s = requests.session()

        _user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
        _accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        _accept_encoding = 'gzip, deflate, br'
        _accept_language = 'en,zh-CN;q=0.8,zh;q=0.6'
        _content_type = 'application/x-www-form-urlencoded'

        # Todo 多次登陆，会导致 豆瓣forbidden, 加上Content-Type，application/x-www-form-urlencoded 后次第一次可以运行
        # 但是后面继续 访问又会forbidden,

        self.headers = {
            'User-Agent': _user_agent,
            'Accept': _accept,
            'Accept-Encoding': _accept_encoding,
            'Accept-Language': _accept_language,
            'Content-Type': _content_type
            }

        self.auth = {
            'source': None,
            'redir': self.REDIR,
            'form_email': '',
            'form_password': '',
            'login': self.LOGIN_FLAG
        }

        self.captcha, self.captcha_id = self.search_captcha()
        if self.captcha is not None and self.captcha_id is not None:
            self.solution = self.read_captcha(self.captcha)
            self.auth['captcha-solution'] = self.solution
            self.auth['captcha-id'] = self.captcha_id

    def __del__(self):
        self.s.close()

    def _text_login_url(self):
        html = self.s.post(self.url, headers=self.headers)
        return BeautifulSoup(html.text, "html.parser")

    def search_captcha(self):
        _captcha = self._text_login_url()
        _captcha_imag_list = _captcha.find_all(name='img',
                                               attrs={'alt': 'captcha', 'class': 'captcha_image',
                                                      'id': 'captcha_image'})

        _captcha_id_list = _captcha.find_all(name='input', attrs={'type': 'hidden', 'name': 'captcha-id'})

        if len(_captcha_imag_list) == 1 and len(_captcha_id_list) == 1:
            _captcha_imag_data = _captcha_imag_list[0]
            _captcha_id_data = _captcha_id_list[0]

            if hasattr(_captcha_imag_data, "src") and hasattr(_captcha_id_data, 'value'):
                return _captcha_imag_data.get('src'), _captcha_id_data.get('value')
            else:
                raise ValueError
        else:
            return None, None

    def _download_captcha(self, src, filename):
        return request.urlretrieve(src, filename=filename)

    def read_captcha(self, src):
        abs_filename = os.path.join(os.path.dirname('__file__'), 'resource/captcha.png')
        self._download_captcha(src, filename=abs_filename)
        message = 'pls open the {0} and input the character: '.format(abs_filename)
        data = input(message)
        if data:
            return data

    def _prepare_login(self, user, password):
        self.auth['form_email'] = user
        self.auth['form_password'] = password
        return self.auth

    def login(self, user, password):
        self._prepare_login(user, password)
        rs = self.s.post(self.url, headers=self.headers, data=self.auth)

        if rs.status_code == 200 and rs.url == self.REDIR:
            self.islogin = True
            return self.s
        else:
            rs.raise_for_status()


class DouBanPeopleCrawl(DouBanAuth):
    PEOPLE_PATTERN = 'https://www\.douban\.com/people/\w+/$'

    def __init__(self):
        super(DouBanPeopleCrawl, self).__init__()
        self.cache = set()
        self._handle_cache = set()

    def crawl_people_href(self, url=DouBanAuth.INDEX_URL, maxcount=100):
        """
        :param url:
        :param maxcount: It do not mean how many people you should crawl, it accurate mean at least!
        so the cache's number may be more than maxcount
        :return: cache
        """
        if not self.islogin:
           raise DouBanNotLoginError

        html = self.s.post(url, headers=self.headers)
        bs = BeautifulSoup(html.text, "html.parser")
        for element in bs.find_all(name='a', attrs={'href': re.compile(self.PEOPLE_PATTERN)}):
            # print("add the {} into cache".format(element.get('href')))
            self.cache.add(element.get('href'))

        if len(self.cache) < maxcount:
            for url in self.cache - self._handle_cache:
                self._handle_cache.add(url)
                return self.crawl_people_href(url, maxcount)

        return self.cache

    def clear_cache(self):
        return self.cache.clear()


class DouBanPeopleAlbumCrawl(DouBanPeopleCrawl):
    PHOTO_FLAG = 'photos'
    ALUBM_PATTERN = 'https://www\.douban\.com/photos/album/\w+/$'

    def __init__(self):
        super(DouBanPeopleAlbumCrawl, self).__init__()

    def crawl_people_album(self):
        if not self.cache:
            raise DouBanCrawlNotCallError

        for url in map(lambda x: x+self.PHOTO_FLAG, self.cache):
            html = requests.post(url, headers=self.headers)
            # 由于self.s 是session实例 所以这边调用self.s.post的话 response 的页面会跳转redir 定义的
            # 所有这边直接调用 request.post 方法.
            bs = BeautifulSoup(html.text, "html.parser")
            for element in bs.find_all(name='a', attrs={'href': re.compile(self.ALUBM_PATTERN),
                                                        'class': 'album_photo'}):
                yield element.get('href')


class DouBanPeoplePhotosCrawl(DouBanPeopleAlbumCrawl):
    PHOTOLST_PATTERN = 'https://www\.douban\.com/photos/photo/\w+/$'
    PHOTO_PATTERN = 'https://www\.douban\.com/photos/photo/\w+'

    def __init__(self):
        super(DouBanPeoplePhotosCrawl, self).__init__()

    def _craw_people_photos(self):
        for album in self.crawl_people_album():
            html = requests.post(album, headers=self.headers)
            bs = BeautifulSoup(html.text, "html.parser")
            for element in bs.find_all(name='a', attrs={'href': re.compile(self.PHOTOLST_PATTERN),
                                                        'class': 'photolst_photo'}):
                yield element.get('href')

    def crawl_photo(self):
        for photo in self._craw_people_photos():
            html = requests.post(photo, headers=self.headers)
            bs = BeautifulSoup(html.text, "html.parser")
            for element in bs.find_all(name='a', attrs={'class': 'mainphoto', 'href': re.compile(self.PHOTO_PATTERN)}):
                for url in element.find_all(name='img'):
                    yield url.get('src')


def download(url, location=None):
    location = os.path.join(os.path.dirname('__file__'), 'resource/img/') if not location else location
    item = request.urlparse(url)
    name = item.path.split('/')[-1]
    download_file = os.path.join(location, name)
    request.urlretrieve(url, filename=download_file)

"""
Usage:
c = DouBanPeoplePhotosCrawl()
c.login('xxxxx', 'yyyyy')
c.crawl_people_href(maxcount=100) # to genrate cache data.
for i in c.crawl_photo():
    download(i)
"""