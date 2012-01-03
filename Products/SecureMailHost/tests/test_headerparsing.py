#
# Tests the email validation
#

from common import SMHTestCase

import email.Message
from Products.SecureMailHost import mail

tests = []

class TestHeaderParsing(SMHTestCase):

    def test_header_cc_bcc(self):
        # test if cc and bcc addresses are added to the server To
        send = self.mailhost.secureSend

        msg = email.MIMEText.MIMEText('body', 'plain', 'us-ascii')
        mto =  "to@example.org"
        mfrom = "from@example.org"
        mbcc = "bcc@example.org"
        mcc = "cc@example.org"

        result = send(msg, mto=mto, mfrom=mfrom, subject='test',
                      mcc=mcc, mbcc = mbcc, debug=True)

        self.failUnless(isinstance(result, mail.Mail),
                        'Result is not a mail.Mail instance')

        eto = ",".join(result.mto)
        msg = result.message

        for addr in mto, mbcc, mcc:
            if eto.find(addr) == -1:
                self.fail("%s not in %s " % (addr, eto))

        self.failUnlessEqual(msg['From'], mfrom)
        self.failUnlessEqual(msg['Cc'], mcc)
        self.failUnlessEqual(msg['Bcc'], mbcc)
        self.failUnlessEqual(msg['To'], mto)

tests.append(TestHeaderParsing)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in tests:
        suite.addTest(makeSuite(test))
    return suite
