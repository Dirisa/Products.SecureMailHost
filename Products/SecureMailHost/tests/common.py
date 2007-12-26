from Testing import ZopeTestCase

ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('PageTemplates', quiet=1)
ZopeTestCase.installProduct('PythonScripts', quiet=1)
ZopeTestCase.installProduct('ExternalMethod', quiet=1)

from Products.SecureMailHost.SecureMailHost import SecureMailBase


class SMHTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.mailhost = SecureMailBase('securemailhost', '')
