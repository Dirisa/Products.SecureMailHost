# -*- coding: iso-8859-1 -*-
#
# Tests the email validation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *
from email.MIMEText import MIMEText
import email.Message
from Products.SecureMailHost.mail import Mail
from Products.SecureMailHost.interfaces import IMail
from Interface.Verify import verifyObject
from DateTime import DateTime

tests = []
msg = """\
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
From: foo@example.com
To: bar@example.com
Subject: foo bar

foo body"""

class TestMail(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        ZopeTestCase.ZopeTestCase.afterSetUp(self)
        msg = MIMEText('foo body')
        msg['From'] = 'foo@example.com'
        msg['To'] = 'bar@example.com'
        msg['Subject'] = 'foo bar'
        self.msg = msg
        self.mail = Mail('foo@example.com', 'bar@example.com', self.msg, bar='foo')
        
    def test_basemessage(self):
        msgstr = self.msg.as_string()
        self.failUnlessEqual(msgstr, msg)
        
    def test_interface(self):
        verifyObject(IMail, self.mail)
        
    def test_init(self):
        mail = self.mail
        self.failUnlessEqual(mail.mfrom, 'foo@example.com')
        self.failUnlessEqual(mail.mto, 'bar@example.com')
        self.failUnlessEqual(mail.kwargs, {'bar':'foo'})
        self.failUnlessEqual(mail.host, 'localhost')
        self.failUnlessEqual(mail.port, 25)
        self.failUnlessEqual(mail.id, None)
        mail.setId('id')
        self.failUnlessEqual(mail.id, 'id')
        self.failUnlessEqual(mail.errors, 0)
        self.failUnlessEqual(mail.getErrors(), 0)
        mail.incError()
        self.failUnlessEqual(mail.getErrors(), 1)
        
    def test_dategen(self):
        mail = self.mail
        date = mail.message['Date']
        self.failUnless(date)
        self.failUnless(DateTime(date))
    
    def test_messsageid(self):
        mail = self.mail
        msgid = mail.message['Message-Id']
        self.failUnless(msgid)
        
    def test_str(self):
        mail = self.mail
        self.failUnlessEqual(str(mail), mail.message.as_string())
        
tests.append(TestMail)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in tests:
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
