#!/bin/python3.5
#coding: utf-8
from smtplib import SMTP
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailClient(object):
    smtp_server = ''
    account = ''
    passwd = ''
    __mail = None

    def __init__(self, smtp_server='', account='', passwd=''):
        self.smtp_server = smtp_server
        self.account = account
        self.passwd = passwd
        self.__mail = MIMEMultipart('alternative')
        self.__mail['From'] = account

    def add_content(self, content, type_):
        if type_ == 'text':
            mime_type = 'plain'
        elif type_ == 'html':
            mime_type = 'html'
        else:
            raise TypeError('unsupported type')
        self.__mail.attach(MIMEText(content, mime_type))

    def set_subject(self, subject):
        self.__mail['Subject'] = subject

    def set_recipient(self, to_):
        self.__mail['To'] = to_

    def set_sender(self, from_):
        self.__mail['From'] = from_

    def send(self, need_auth=False):
        with SMTP(self.smtp_server) as s:
            if need_auth:
                s.login(self.account, self.passwd)
            s.send_message(self.__mail)
