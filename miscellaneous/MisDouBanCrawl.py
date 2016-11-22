#! -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
from urllib import request
import os
import re
from miscellaneous.MisExceptions import DouBanNotLoginError, DouBanCrawlNotCallError

# main_url = 'https://www.douban.com'
# login_url = 'https://accounts.douban.com/login'
# mail_url= 'https://www.douban.com/doumail'
# people_index_url = 'https://www.douban.com/people'
#
#
# user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
# accept =  'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
# accept_encoding = 'gzip, deflate, br'
# accept_language = 'en,zh-CN;q=0.8,zh;q=0.6'
#
# my_header = {
#     'User-Agent' : user_agent,
#     'Accept'     : accept,
#     'Accept-Encoding' : accept_encoding,
#     'Accept-Language' : accept_language
# }
#
# params = {
#     'source'        :    None,
#     'redir'         :   'https://www.douban.com',
#     'form_email'    :   'xxxxxx',
#     'form_password' :   'xxxxxx',
#     'login'         :   '登录'
# }
#
# html = requests.post(login_url)
# captcha_url = ''
# captcha_id  = ''
# bs = BeautifulSoup(html.text)
# for i in bs.find_all(name='img', attrs={'alt':'captcha', 'class':'captcha_image', 'id':'captcha_image'}):
#     print(i)
#     if hasattr(i, 'src'):
#         captcha_url = i.get('src')
#
# for i in bs.find_all(name='input', attrs={'type':'hidden', 'name':'captcha-id'}):
#     print(i)
#     if hasattr(i, 'value'):
#         captcha_id = i.get('value')
#
# print(captcha_url)
# request.urlretrieve(captcha_url, filename='./captcha.png')
#
# answer = input('pls enter the character in the captcha.png: ')
# params['captcha-solution'] = answer
# params['captcha-id'] = captcha_id
# print(params)
#
#
# # r = requests.get(url)
# # bs = BeautifulSoup(r.content)
# # for i in bs.find_all(name='a'):
# #     print(i)
# s = requests.session()
# #
# #
# rs = s.post(login_url, headers=my_header, data=params)
# print(rs.url, rs.status_code, rs.history)
#
# ms = s.post(mail_url)
# print(ms.status_code)





class DouBanAuth(object):
    INDEX_URL = REDIR = 'https://www.douban.com'
    LOGIN_URL = 'https://accounts.douban.com/login'
    LOGIN_FLAG = '登录'

    def __init__(self, url=None):
        self.url = url if url else self.LOGIN_URL
        self.islogin = False
        self.s = requests.session()


        _user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
        _accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        _accept_encoding = 'gzip, deflate, br'
        _accept_language = 'en,zh-CN;q=0.8,zh;q=0.6'

        self.headers = {
            'User-Agent' : _user_agent,
            'Accept'     : _accept,
            'Accept-Encoding' : _accept_encoding,
            'Accept-Language' : _accept_language
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
        html = self.s.get(self.url, headers=self.headers)
        return BeautifulSoup(html.text, "html.parser")


    def search_captcha(self):
        _captcha = self._text_login_url()
        _captcha_imag_list = _captcha.find_all(name='img',
                                               attrs={'alt':'captcha', 'class':'captcha_image',
                                                      'id':'captcha_image'})

        _captcha_id_list = _captcha.find_all(name='input', attrs={'type':'hidden', 'name':'captcha-id'})

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
        if not self.islogin:
            raise DouBanNotLoginError

        html = self.s.post(url, headers=self.headers)
        bs = BeautifulSoup(html.text, "html.parser")
        for element in bs.find_all(name='a', attrs={'href':re.compile(self.PEOPLE_PATTERN)}):
            # print("add the {} into cache".format(element.get('href')))
            self.cache.add(element.get('href'))

        if len(self.cache) < maxcount:
            for i in self.cache - self._handle_cache:
                self._handle_cache.add(i)
                return self.crawl_people_href(i, maxcount)

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

        for i in map(lambda x: x+self.PHOTO_FLAG, self.cache):
            print(i)
            html = self.s.post(i, headers=self.headers)
            bs = BeautifulSoup(html.text, "html.parser")
            for element in bs.find_all(name='a', attrs={'class': 'album_photo',
                                                        'href': re.compile(self.ALUBM_PATTERN)}):
                yield element.get('href')


class DouBanPeoplePhotosCrawl(DouBanPeopleAlbumCrawl):
    PHOTO_PATTERN = 'https://www\.douban\.com/photos/photo/\w+'

    def __init__(self):
        super(DouBanPeoplePhotosCrawl, self).__init__()
        self.photo_list = set()
        self.photos = set()

    def _craw_people_photos(self):
        for album in self.crawl_people_album():
            html = self.s.post(album, headers=self.headers)
            bs = BeautifulSoup(html.text, "html.parser")
            for element in  bs.find_all(name='a', attrs={'href': re.compile(self.PHOTO_PATTERN),
                                                         'class': 'photolst_photo'}):
                self.photo_list.add(element.get('href'))
        return self.photo_list

    def crawl_photo(self):
        for photo in self._craw_people_photos():
            html = self.s.post(photo, headers=self.headers)
            bs = BeautifulSoup(html.text, "html.parser")
            for element  in bs.find_all(name='a', attrs={'class': 'mainphoto',
                                         'href': re.compile(self.PHOTO_PATTERN)}):
                for url in element.find_all(name='img'):
                    self.photos.add(url.get('src'))
        return self.photos


c = DouBanPeoplePhotosCrawl()
c.login('289557306@qq.com', 'm64628288')
c.crawl_people_href(maxcount=30)

for i in c.crawl_people_album():
    print(i)






