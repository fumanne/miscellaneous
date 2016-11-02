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
from .MisExceptions import MailError
from .MisExceptions import MailTypeError


class BaseSendEmail(object):
    COMMSPACE = ', '

    def __init__(self, host, port=25):
        self.host = host
        self.port = port
        self.status = None
        self.mail_server = None

    @staticmethod
    def validate(param, check):
        if isinstance(param, check):
            return True
        else:
            raise MailTypeError("Error type for {0}".format(param))

    def sends(self, from_users, to_users, cc_users=None, mail_body=None, mail_subject=None, mail_attach=None):
        """
        :param from_users: type ==> str
        :param to_users: type ==> list
        :param cc_users: type ==> list
        :param mail_body:    type ==> str
        :param mail_subject:  type ==> str
        :param mail_attach:  type ==> list
        :return: status
        """

        self.validate(from_users, str)
        self. validate(to_users, list)
        if cc_users:
            self.validate(cc_users, list)

        self.validate(mail_body, str)
        self.validate(mail_subject, str)
        if mail_attach:
            self.validate(mail_attach, list)

        msg = MIMEMultipart()
        mail_text = MIMEText(mail_body, 'plain', 'utf-8')

        msg['From'] = from_users
        msg['To'] = BaseSendEmail.COMMSPACE.join(to_users)
        msg['Cc'] = BaseSendEmail.COMMSPACE.join(cc_users)
        msg['Subject'] = mail_subject
        msg.attach(mail_text)
        for file in mail_attach:
            ctype, encoding = mimetypes.guess_type(file)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split('/', 1)

            if maintype == 'text':
                with open(file) as fp:
                    attach = MIMEText(fp.read(), _subtype=subtype)
            elif maintype == "image":
                with open(file, 'rb') as fp:
                    attach = MIMEImage(fp.read(), _subtype=subtype)
            elif maintype == "audio":
                with open(file, 'rb') as fp:
                    attach = MIMEAudio(fp.read(), _subtype=subtype)
            else:
                with open(file, 'rb') as fp:
                    attach = MIMEBase(maintype, subtype)
                    # TODO: if the attach file's type like .mkv .mp4 it will failed when set_payload, fix it!
                    attach.set_payload(fp.read())
                    encode_base64(attach)
            attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
            msg.attach(attach)

        composed = msg.as_string()
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
