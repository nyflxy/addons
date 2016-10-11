# -*- coding: utf-8 -*-
#
# @author: Daemon Wang
# Created on 2016-03-02
#

import re
import logging
import smtplib
import time
import pdb
from datetime import datetime, timedelta
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email.utils import formatdate

from tornado.escape import utf8
from tornado.options import options

__all__ = ("send_email", "EmailAddress")

# borrow email re pattern from django
_email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain


def send_email(fr, to, subject, body, html=None, attachments=[]):
    """Send an email.

    If an HTML string is given, a mulitpart message will be generated with
    plain text and HTML parts. Attachments can be added by providing as a
    list of (filename, data) tuples.
    """
    # convert EmailAddress to pure string
    if isinstance(fr, EmailAddress):
        fr = str(fr)
    else:
        fr = utf8(fr)
    to = [utf8(t) for t in to]
    if html:
        # Multipart HTML and plain text
        message = MIMEMultipart("alternative")
        message.attach(MIMEText(body, "plain"))
        message.attach(MIMEText(html, "html",'gb18030'))
    else:
        # Plain text
        message = MIMEText(body)
    if attachments:
        part = message
        message = MIMEMultipart("mixed")
        message.attach(part)
        for a in attachments:
            # part = MIMEBase("application", "octet-stream")
            fp = open(a['data'],'rb')
            part = MIMEBase('application','vnd.ms-excel')
            part.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment",
                filename=a['filename'].encode('gb2312'))
            message.attach(part)

    message["Date"] = formatdate(time.time())
    message["From"] = fr
    message["To"] = COMMASPACE.join(to)
    message["Subject"] = utf8(subject)

    _get_session().send_mail(fr, to, utf8(message.as_string()))


class EmailAddress(object):
    def __init__(self, addr, name=""):
        assert _email_re.match(addr), "Email address(%s) is invalid." % addr

        self.addr = addr
        if name:
            self.name = name
        else:
            self.name = addr.split("@")[0]

    def __str__(self):
        return '%s <%s>' % (utf8(self.name), utf8(self.addr))


class _SMTPSession(object):
    def __init__(self, host, user='', password='', duration=30, tls=False):
        self.host = host
        self.user = user
        self.password = password
        self.duration = duration
        self.tls = tls
        self.session = None
        self.deadline = datetime.now()
        self.renew()

    def send_mail(self, fr, to, message):
        if self.timeout:
            self.renew()

        try:
            self.session.sendmail(fr, to, message)
        except Exception as e:
            err = "Send email from %s to %s failed!\n Exception: %s!" \
                % (fr, to, e)
            import traceback
            print (traceback.format_stack())
            logging.error(err)
            self.renew()

    @property
    def timeout(self):
        if datetime.now() < self.deadline:
            return False
        else:
            return True

    def renew(self):
        try:
            if self.session:
                self.session.quit()
        except Exception:
            pass

        self.session = smtplib.SMTP(self.host)
        if self.user and self.password:
            if self.tls:
                self.session.starttls()

            self.session.login(self.user, self.password)

        self.deadline = datetime.now() + timedelta(seconds=self.duration * 60)

# smtp = {"host": "smtp.exmail.qq.com",
#         "user": "admin@dhui100.com",
#         "password": "You1234567",
#         "duration": 30,
#         "tls": True
#         }

smtp = {
    "host": "mail.dhjt.com",
    # "host": "192.168.1.98",
    "user": "nj.niyoufa@dhjt.com",
    "password": "19922011nyf",
    "duration": 30,
    "tls": True
}

def _get_session():
    global _session
    if _session is None:
        _session = _SMTPSession(smtp['host'],
                                smtp['user'],
                                smtp['password'],
                                smtp['duration'],
                                smtp['tls'])

    return _session

_session = None

if __name__ == "__main__":

    send_email('nj.niyoufa@dhjt.com', ["nj.heshan@dhjt.com"], "测试excel文件邮件发送", '',
           html=u'<p>%s</p><p>日期：%s - %s</p>' % (u"测试excel文件邮件发送", u"2015", u"2016"),
           attachments=[{"filename": u"测试excel文件邮件发送.xls", "data": u"/home/dhui100/倪有发——工作日报.xls"}])
