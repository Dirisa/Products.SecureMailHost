# -*- coding: iso-8859-1 -*-
#
# Tests the email validation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *
from Products.SecureMailHost.mailqueue import MailQueue
from Products.SecureMailHost.mailqueue import AnyDBMailStorage
from Products.SecureMailHost.mailqueue import TransactionalMailQueue
from Products.SecureMailHost.interfaces import IMailQueue
from Products.SecureMailHost.interfaces import IDataManager

from Interface.Verify import verifyObject

tests = []

class TestMailQueue(ZopeTestCase.ZopeTestCase):
    
    def afterSetUp(self):
        ZopeTestCase.ZopeTestCase.afterSetUp(self)
        self.obj = MailQueue()
        
    def test_interface(self):
        verifyObject(IMailQueue, self.obj)
        
tests.append(TestMailQueue)


class TestAnyDBQueue(TestMailQueue):
    
    def afterSetUp(self):
        TestMailQueue.afterSetUp(self)
        self.obj = AnyDBMailStorage()
        
tests.append(TestAnyDBQueue)


class TestTransactionalMailQueue(TestMailQueue):
    
    def afterSetUp(self):
        TestMailQueue.afterSetUp(self)
        self.obj = TransactionalMailQueue()
        
    def test_interface(self):
        TestMailQueue.test_interface(self)
        verifyObject(IDataManager, self.obj)
        
tests.append(TestTransactionalMailQueue)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in tests:
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
