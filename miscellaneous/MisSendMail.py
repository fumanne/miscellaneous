#! -*- coding: utf-8 -*-

import smtplib
import os
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
import mimetypes
from miscellaneous.MisExceptions import MailError
from miscellaneous.MisExceptions import MailTypeError


class BaseSendEmail(object):
    COMMSPACE = ', '

    def __init__(self, host, port=25):
        self.host = host
        self.port = port
        self.status = None
        self.mail_server = None
        self.msg = MIMEMultipart()

    @staticmethod
    def validate(param, check):
        if isinstance(param, check):
            return True
        else:
            raise MailTypeError("Error type for {0}".format(param))


    def generate_from(self, from_user):
        if self.validate(from_user, str):
            self.msg['From'] = from_user

    def generate_to(self, to_users):
        if self.validate(to_users, str):
            self.msg['To'] = to_users

        if self.validate(to_users, (list, tuple)):
            self.msg['To'] = self.COMMSPACE.join(to_users)

    def generate_cc(self, cc_users=None):
        if self.validate(cc_users, str):
            self.msg['Cc'] = cc_users

        if self.validate(cc_users, (list, tuple)):
            self.msg['Cc'] = self.COMMSPACE.join(cc_users)

    def generate_subject(self, mail_subject):
        if self.validate(mail_subject, str):
            self.msg['Subject'] = mail_subject


    def generate_body(self, mail_body):
        if self.validate(mail_body, str):
            mail_body = mail_body
        elif hasattr(mail_body, 'read'):
            mail_body = mail_body.read()

        body = MIMEText(mail_body, 'plain', 'utf-8')
        self.msg.attach(body)


    def generate_attach(self, mail_attach):
        if self.validate(mail_attach, str):
            ctype, encoding = mimetypes.guess_type(mail_attach)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split('/', 1)

            if maintype == 'text':
                with open(mail_attach) as fp:
                    attach = MIMEText(fp.read(), _subtype=subtype)
            elif maintype == "image":
                with open(mail_attach, 'rb') as fp:
                    attach = MIMEImage(fp.read(), _subtype=subtype)
            elif maintype == "audio":
                with open(mail_attach, 'rb') as fp:
                    attach = MIMEAudio(fp.read(), _subtype=subtype)
            else:
                with open(mail_attach, 'rb') as fp:
                    attach = MIMEBase(maintype, subtype)
                    attach.set_payload(fp.read())
                    encode_base64(attach)

            attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(mail_attach))
            self.msg.attach(attach)



    def sends(self, from_users, to_users, cc_users=None, mail_body=None, mail_subject=None, mail_attach=None):
        """
        :param from_users: type ==> str
        :param to_users: type ==> str, list, tuple
        :param cc_users: type ==> str, list, tuple
        :param mail_body:    type ==> str, file-object
        :param mail_subject:  type ==> str
        :param mail_attach:  type ==> str, list, tuple
        :return: status
        """
        self.generate_from(from_users)
        self.generate_to(to_users)
        if cc_users:
            self.generate_cc(cc_users)
        if mail_subject:
            self.generate_subject(mail_subject)
        if mail_body:
            self.generate_body(mail_body)
        if mail_attach and isinstance(mail_attach, str):
            self.generate_attach(mail_attach)
        elif mail_attach and isinstance(mail_attach, (list, tuple)):
            for file in mail_attach:
                self.generate_attach(file)

        composed = self.msg.as_string()
        try:
            self.mail_server = smtplib.SMTP(self.host, self.port)
            self.mail_server.sendmail(from_users, to_users, composed)
        except:
            self.status = "Failed"
            raise MailError('Send Mail or Connect Mail Server is Failed')
        else:
            print("Send Mail Successfully")
            self.status = "OK"

    # TODO:  add more function like login, Reciever, or split the mail content  into  independent type!
    @property
    def sends_status(self):
        return self.status

    def __del__(self):
        self.mail_server.close()
