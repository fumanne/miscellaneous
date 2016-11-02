#! -*- coding: utf-8 -*-


class MailError(Exception):
    """ the connect mail exception """
    pass


class MailTypeError(Exception):
    """ the mail type exception """
    pass


class FtpConnectError(Exception):
    """ the connection ftp exception """
    pass

class FtpLoginError(Exception):
    """ the login of ftp exception """
    pass

class FtpDownloadError(Exception):
    """ Downlaod file with ftp exception """
    pass

class FtpUploadError(Exception):
    """ Upload file with ftp exception """
    pass

class DBError(Exception):
    """ DB running exception """
    pass

class SocketGetError(Exception):
    """ parse hostname to ip  with Socket module exception """
    pass

class IPFormatterError(Exception):
    """ IP Formatter exception """
    pass

class FileNotFoundError(Exception):
    """ File is not Found exception """
    pass

class IP2CountryStatusError(Exception):
    """ Status is None exception """
    pass

class XMLParseError(Exception):
    """
    Parse the xml exception
    """
    pass

