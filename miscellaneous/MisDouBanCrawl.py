#! -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import requests
from urllib import request
import os


main_url = 'https://www.douban.com'
login_url = 'https://accounts.douban.com/login'
mail_url= 'https://www.douban.com/doumail'
people_index_url = 'https://www.douban.com/people'


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
accept =  'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
accept_encoding = 'gzip, deflate, br'
accept_language = 'en,zh-CN;q=0.8,zh;q=0.6'

my_header = {
    'User-Agent' : user_agent,
    'Accept'     : accept,
    'Accept-Encoding' : accept_encoding,
    'Accept-Language' : accept_language
}

params = {
    'source'        :    None,
    'redir'         :   'https://www.douban.com',
    'form_email'    :   'xxxxxx',
    'form_password' :   'xxxxxx',
    'login'         :   '登录'
}

html = requests.post(login_url)
captcha_url = ''
captcha_id  = ''
bs = BeautifulSoup(html.text)
for i in bs.find_all(name='img', attrs={'alt':'captcha', 'class':'captcha_image', 'id':'captcha_image'}):
    print(i)
    if hasattr(i, 'src'):
        captcha_url = i.get('src')

for i in bs.find_all(name='input', attrs={'type':'hidden', 'name':'captcha-id'}):
    print(i)
    if hasattr(i, 'value'):
        captcha_id = i.get('value')

print(captcha_url)
request.urlretrieve(captcha_url, filename='./captcha.png')

answer = input('pls enter the character in the captcha.png: ')
params['captcha-solution'] = answer
params['captcha-id'] = captcha_id
print(params)


# r = requests.get(url)
# bs = BeautifulSoup(r.content)
# for i in bs.find_all(name='a'):
#     print(i)
s = requests.session()
#
#
rs = s.post(login_url, headers=my_header, data=params)
print(rs.url, rs.status_code, rs.history)

ms = s.post(mail_url)
print(ms.status_code)





class DouBanCrawl(object):
    INDEX_URL = REDIR = 'https://www.douban.com'
    LOGIN_URL = 'https://accounts.douban.com/login'
    LOGIN_FLAG = '登录'

    def __init__(self, url=INDEX_URL):
        self.url = url
        self.login_status = 0
        self.auth = {
            'source': None,
            'redir': DouBanCrawl.REDIR,
            'form_email': '',
            'form_password': '',
            'login': DouBanCrawl.LOGIN_FLAG
        }

        if self._isNeedCaptcha:
            self.captcha, self.captcha_id = self.search_captcha()
            self.solution = self.read_captcha(self.captcha)
            self.auth['captcha-solution'] = self.solution
            self.auth['captcha-id'] = self.captcha_id

        self.s = requests.session()

    @property
    def _isNeedCaptcha(self):
        return self.search_captcha() is not None

    def text_login_url(self, url=LOGIN_URL):
        html = requests.post(url)
        return BeautifulSoup(html.text)

    def search_captcha(self):
        _captcha_imag_list = self.text_login_url().find_all(name='img',
                                                          attrs={'alt':'captcha', 'class':'captcha_image',
                                                                 'id':'captcha_image'})

        _captcha_id_list = self.text_login_url().find_all(name='input',
                                                             attrs={'type':'hidden', 'name':'captcha-id'})

        if len(_captcha_imag_list) == 1 and len(_captcha_id_list) == 1:
            _captcha_imag_data = _captcha_imag_list[0]
            _captcha_id_data = _captcha_id_list[0]

            if hasattr(_captcha_imag_data, "src") and hasattr(_captcha_id_data, 'value'):
                return _captcha_imag_data.get('src'), _captcha_id_data.get('value')
            else:
                raise ValueError
        else:
            return None

    def _download_captcha(self, src, filename):
        return request.urlretrieve(src, filename=filename)

    def read_captcha(self, src):
        abs_filename = os.path.join((os.path.dirname('__file__'), 'resource/captcha.png'))
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
        rs = self.s.post(DouBanCrawl.LOGIN_URL, data=self.auth)
        if rs.status_code == 200 and rs.url == DouBanCrawl.REDIR:
            self.login_status = 1
            return "OK"
        else:
            rs.raise_for_status()



