#
# Tests the email validation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *
from DateTime import DateTime

buergschaft_latin1_in = open('in/buergschaft.txt', 'rb').read()
buergschaft_utf8_in = unicode(buergschaft_latin1_in, 'latin-1').encode('utf-8')
loremipsum_in = open('in/loremipsum.txt', 'rb').read()

buergschaft_latin1_out = open('out/buergschaft.txt', 'rb').read()
buergschaft_utf8_out = open('out/buergschaft_utf8.txt', 'rb').read()
loremipsum_out = open('out/loremipsum.txt', 'rb').read()


class TestMessage(ZopeTestCase.ZopeTestCase):
    """base message test
    """
    name    = 'no test'
    message = ''
    out     = ''
    subject = 'empty'
    charset = 'us-ascii'
    subtype = 'plain'
    out     = ''
    mfrom   = 'from@example.org'
    mto     = 'to@example.org'
    mcc     = None
    mbcc    = None
    addHeaders = {}

    def afterSetUp(self):
        self.mailhost = SecureMailBase('securemailhost', '')

    def testMessage(self):
        """
        """
        send = self.mailhost.secureSend
        kwargs = self.addHeaders
        kwargs['Date'] = DateTime(0).rfc822()
        result = send(self.message, self.mto, self.mfrom, subject=self.subject,
                      mcc=self.mcc, mbcc = self.mbcc,
                      subtype=self.subtype, charset=self.charset,
                      debug=True,
                      **self.addHeaders)
        mfrom, mto, msg = result
        msgstr = msg.as_string()
        self.failUnlessEqual(self.mto, mto)
        self.failUnlessEqual(self.mfrom, mfrom)
        self.failUnlessEqual(msgstr, self.out)

tests = []

class TestBuergschaftLatin1(TestMessage):
    name    = 'buergschaft_latin'
    message = buergschaft_latin1_in
    out     = buergschaft_latin1_out

    subject = 'Die Buergschaft'
    charset = 'latin-1'
    subtype = 'plain'
    out     = buergschaft_latin1_out

tests.append(TestBuergschaftLatin1)

class TestBuergschaftUTF8(TestMessage):
    name    = 'buergschaft_uft8'
    message = buergschaft_utf8_in
    out     = buergschaft_utf8_out

    subject = 'Die Buergschaft'
    charset = 'utf8'
    subtype = 'plain'
    out     = buergschaft_utf8_out

tests.append(TestBuergschaftUTF8)

class TestLoremIpsum(TestMessage):
    name    = 'loremipsum'
    message = loremipsum_in
    out     = loremipsum_out

    subject = 'Lorem Ipsum'
    charset = 'ascii'
    subtype = 'plain'
    out     = loremipsum_out

tests.append(TestLoremIpsum)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in tests:
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
