#! -*- coding: utf-8 -*-
import ftplib
import socket
import os
from .MisExceptions import FtpConnectError
from .MisExceptions import FtpLoginError
from .MisExceptions import FtpDownloadError
from .MisExceptions import FtpUploadError


class BaseFtp(object):
    CONNECT_STATUS = {0: 'OK', 1: 'Failed', 2: 'Processing', 3: "Preparing"}
    LOGIN_STATUS = {0: 'OK', 1: 'Failed', 2: 'Processing', 3: "Preparing"}

    def __init__(self, ftp_host, ftp_user, ftp_password, ftp_port):
        self.ftp_host = ftp_host
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.ftp_port = ftp_port
        self.myftp = None
        self.connect_status = BaseFtp.CONNECT_STATUS[3]
        self.login_status = BaseFtp.LOGIN_STATUS[3]

    def connect(self):
        self.myftp = ftplib.FTP()
        try:
            self.myftp.connect(self.ftp_host, self.ftp_port)
        except socket.error:
            self.connect_status = BaseFtp.CONNECT_STATUS[1]
            raise FtpConnectError("Connect {} failed".format(self.ftp_host))
        else:
            self.connect_status = BaseFtp.CONNECT_STATUS[0]
            return self.myftp

    def login(self):
        if self.connect_status == 'OK':
            try:
                self.myftp.login(self.ftp_user, self.ftp_password)
            except ftplib.error_perm:
                self.login_status = BaseFtp.LOGIN_STATUS[1]
                raise FtpLoginError("Login ftp server {} Failed".format(self.ftp_host))
            else:
                self.login_status = BaseFtp.LOGIN_STATUS[0]
                return self.myftp

    @property
    def dir(self):
        return self.myftp.dir()

    @property
    def pwd(self):
        return self.myftp.pwd()

    def cwd(self, path):
        try:
            self.myftp.cwd(path)
        except ftplib.error_perm as e:
            print(e)
        else:
            print('Change Path {} Successfully'.format(path))

    def mkd(self, directory):
        try:
            self.myftp.mkd(directory)
        except ftplib.error_perm as e:
            print(e)
        else:
            print("Create Directory {} Successfully".format(directory))

    def rmd(self, directory):
        try:
            self.myftp.rmd(directory)
        except ftplib.error_perm as e:
            print(e)
        else:
            print("Remove Directory {} successfully".format(directory))

    def download(self, file):
        download_file = open(file, "wb").write
        # 根据 ftplib 源码 retrbinary 的第2个参数为callback 方法. 此callback 会将 socket 收到的file data
        # 以参数的形式写入, 所以这边需要将file 的write 方法 取了个download_file 名字.
        try:
            self.myftp.retrbinary('RETR %s' %file, download_file)
        except:
            raise FtpDownloadError('Download {} Failed'.format(file))
        else:
            print("Download {} Successfully".format(file))

    def upload(self, file):
        upload_file = open(file, 'rb')
        try:
            self.myftp.storbinary('STOR %s' % (os.path.basename(file)), upload_file)
        except:
            raise FtpUploadError("Upload {} Failed".format(upload_file))
        else:
            print("Upload {} Successfully".format(file))
        finally:
            upload_file.close()

    def delete(self, file):
        try:
            self.myftp.delete(file)
        except ftplib.error_perm as e:
            print(e)
        else:
            print("Delete {} Successfully".format(file))

    def upload_file_from_dir(self, dirs):
        for root, directory, files in os.walk(dirs):
            for file in files:
                abs_file = os.path.join(root, file)
                self.upload(abs_file)

    def upload_ex(self, srcfile, destfile):
        srcfile_obj = open(srcfile, 'rb')
        try:
            self.myftp.storbinary('STOR %s' % (os.path.basename(destfile)), srcfile_obj)
        except:
            raise FtpUploadError("Upload {} Failed".format(srcfile))
        else:
            print("Upload {0} Successfully to {1}".format(srcfile, destfile))
        finally:
            srcfile_obj.close()

    def nlst(self):
        return self.myftp.nlst()

    # TODO:  add more function using ftplib builtin function

    def __del__(self):
        self.myftp.quit()
