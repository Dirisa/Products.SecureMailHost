# -*- coding: iso-8859-1 -*-
#
# Tests the email validation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from common import *
from email.MIMEText import MIMEText
from Products.SecureMailHost.mailqueue import MailQueue
from Products.SecureMailHost.mailqueue import AnyDBMailStorage
from Products.SecureMailHost.mailqueue import TransactionalMailQueue
from Products.SecureMailHost.mailqueue import mailQueue
from Products.SecureMailHost.mail import Mail
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
        
    def test_isRegisteredInTransaction(self):
        t = get_transaction()
        self.failUnless(self.obj in t._objects,
            'TransactionalMailQueue is not registered in transaction')
            
    def test_mailIsMovedFromTransactionalToPersistentAfterCommit(self):
        global mailQueue
        transaction = get_transaction()
        msg = MIMEText('foo body')
        mail = Mail('foo@example.com', 'bar@example.com', msg)
        mail.setId('aTestMail')
        mailId = mail.getId()
        tq = self.obj
        
        # queue the mail and test if it's in the queue
        tq.queue(mail)
        self.failUnless(tq.has_key(mailId))
        self.failUnless(tq.get(mailId) is mail, (tq.get(mailId), mail))
        
        # now "committing" the transaction for the tq manually
        tq.tpc_vote(transaction) # verify that tq is able to commit the transaction
        self.failUnlessEqual(tq._transaction_voted, True)
        self.failUnlessEqual(tq._transaction_aborted, False)
        tq.commit(tq, transaction) # commit the transaction
        tq.tpc_finish(transaction) # indicate the committed transaction
        
        # after committing a subtransaction the transactional queue should be
        # empty and the mail should be in the persistent mail queue
        self.failUnlessEqual(tq._queue, {})
        self.failUnless(mailQueue.has_key(mailId))
        self.failUnless(mailQueue.get(mailId) is mail)

        
tests.append(TestTransactionalMailQueue)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in tests:
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
