##############################################################################
#
# Copyright (c) 2004 Christian Heimes and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
"""
try:
    True
except NameError:
    True=1
    False=0

from config import DB_FILE

import os
from types import ListType
from types import TupleType
from types import StringType
from UserDict import DictMixin
import time
import anydbm
import threading
import socket
import random
import cPickle as pickle
from zLOG import LOG, INFO, PROBLEM, DEBUG
from interfaces import IMailQueue
from interfaces import IMail
try:
    from ZODB.interfaces import IDataManger
except ImportError:
    from interfaces import IDataManager

try:
    host = socket.gethostname()
except:
    host = str(random.randint(1, 1000000))

class MailQueue(DictMixin):
    """A generic and thread safe mail queue
    
    It's working like a dict except you can't use __setitem__
    """
    
    __implements__ = IMailQueue

    def __init__(self):
        # _queue must be a dict like instance
        self._queue = None
        self._lock = threading.Lock()
    
    def queue(self, mails):
        """Sends one or more emails to the queue
        """
        if type(mails) not in (ListType, TupleType):
            mails = (mails, )
        # assign ids to mails
        for mail in mails:
            assert IMail.isImplementedBy(mail)
            if mail.getId() is None:
                id = self.mkMailId()
                mail.setId(id)
                del id

        try:
            self._lock.acquire()
            for mail in mails:
                id = mail.getId()
                self._add(id, mail)
            self.sync()
        finally:
            self._lock.release()
            
    def _add(self, id, mail):
        """Adds one mail to the queue

        MUST be called within an acquired lock!
        """
        raise NotImplementedException
    
    def __setitem__(self, key, obj):
        """__setitem__ is not supported!
        """
        raise RuntimeError, '__setitem__ is not supported. Use queue()'
        
    def __getitem__(self, id):
        """Get a mail by id
        """
        try:
            self._lock.acquire()
            return self._get(id)
        finally:
            self._lock.release()
            
    def _get(self, id):
        """Gets one mail from the queue
        
        MUST raise a KeyError when the key is not in the queue

        MUST be called within an acquired lock!
        """
        raise NotImplementedException

    def __delitem__(self, mail_or_id):
        """Removes an email from the queue

        MUST be called within an acquired lock!
        """
        if type(mail_or_id) is StringType:
            id = mail_or_id
        elif IMail.isImplementedBy(mail_or_id):
            id = mail_or_id.getId()
        else:
            raise TypeError, 'Invalid type: %s' % type(mail_or_id)
        assert type(id) is StringType
        try:
            self._lock.acquire()
            self._remove(id)
            self.sync()
        finally:
            self._lock.release()
            
    def _remove(self, id):
        """Removes one mail from the queue

        MUST be called within an acquired lock!
        """
        raise NotImplementedException
   
    def sync(self):
        """syncs the queue
        
        Useful to sync a DB in the filesystem

        MUST be called within an acquired lock!
        """
        pass
    
    def mkMailId(self):
        """Generates a id
        
        MUST be called within an acquired lock!
        """
        global host
        count = 0
        while True:
            ts = time.time()
            rand = random.randint(1, 1000000)
            id = '%s-%s-%i-%i' % (ts, host, rand, count)
            if id not in self._queue.keys():
                return id
            else:
                count+=1
    
    def keys(self):
        """List all mail ids (queue keys)
        """
        try:
            self._lock.acquire()
            return self._queue.keys()
        finally:
            self._lock.release()
            
    def has_key(self, id):
        """Tests if the id is in the queue
        """
        try:
            self._lock.acquire()
            return id in self._queue.keys()
        finally:
            self._lock.release()

    def __len__(self):
        """Thread safe len() method
        """
        try:
            self._lock.acquire()
            return len(self._queue)
        finally:
            self._lock.release()
            
    def __repr__(self):
        return '<%s at %s>' % (self.__class__.__name__, id(self))

class AnyDBMailStorage(MailQueue):
    """Stores Mail objects in a queue.
    
    For safty reasons the emails are pickled on the file system in a seperate db
    to recover them after a zope crash or shutdown.
    
    queue(email)        - adds an email to the queue
    get(id)             - gets an email from the queue by id
    remove(email_or_id) - removes an email from the queue
    
    To increase the performance the unpickled emails are cached in a pickle
    cache.
    """
    
    __implements__ = MailQueue.__implements__

    def __init__(self):
        MailQueue.__init__(self)
        if not os.path.isfile(DB_FILE):
            db = anydbm.open(DB_FILE, 'c')
            db.close()
        self._queue = anydbm.open(DB_FILE, 'w') # write
        self._pickle_cache = {}

    def _fastQueue(self, mails):
        """Fast queue with less checks
        
        Used for moving mails from the transaction aware queue to the persistent
        queue.
        It assumes that:
             * mails is a list
             * all mails are implementing IMail
             * all mails have an id
        """
        assert type(mails) is ListType
        try:
            self._lock.acquire()
            for mail in mails:
                id = mail.getId()
                self._add(id, mail)
            self.sync()
        finally:
            self._lock.release()

    def _add(self, id, mail):
        """Adds one mail to the queue

        MUST be called within an acquired lock!
        """
        # store mail in pickle cache
        self._pickle_cache[id] = mail
        # store pickled mail in db
        dump = pickle.dumps(mail)
        self._queue[id] = dump
        LOG('SecureMailHost', DEBUG, 'Mail queued: %s' % mail.info())
        
    def _get(self, id):
        """Gets one mail from the queue
        
        MUST raise a KeyError when the key is not in the queu

        MUST be called within an acquired lock!
        """
        mail = self._pickle_cache.get(id, None)
        if mail is None:
            dump = self._queue[id]
            mail = pickle.loads(dump)
            self._pickle_cache[id] = mail
        return mail

    def _remove(self, id):
        """Removes one mail from the queue

        MUST be called within an acquired lock!
        """
        del self._queue[id]
        try:
            del self._pickle_cache[id]
        except KeyError:
            pass
   
    def sync(self):
        """syncs the DB in the fs
        
        MUST be called within an acquired lock!
        """
        # sync is not supported by all databases
        sync = getattr(self._queue, 'sync', None)
        if sync is not None:
            sync()
    
mailQueue = AnyDBMailStorage()

class TransactionalMailQueue(MailQueue):
    """A transaction aware mail queue
    """
    
    __implements__ = MailQueue.__implements__, IDataManager

    def __init__(self):
        MailQueue.__init__(self)
        self._queue = {}
        self._transaction_voted = False
        self._transaction_aborted = False
        
        # register self as DataManager in the current transaction
        get_transaction().register(self)

    def _add(self, id, mail):
        """Adds one mail to the queue

        MUST be called within an acquired lock!
        """
        self._queue[id] = mail

    def _get(self, id):
        """Gets one mail from the queue
        
        MUST raise a KeyError when the key is not in the queu

        MUST be called within an acquired lock!
        """
        return self._queue[id]

    def _remove(self, id):
        """Removes one mail from the queue

        MUST be called within an acquired lock!
        """
        del self._queue[id]

    # ZODB transaction api from IDataManager

    def abort_sub(self, transaction):
        """Discard all subtransaction data.
        """

    def commit_sub(self, transaction):
        """Commit all changes made in subtransactions and begin 2-phase commit
        """
        pass

    def tpc_begin(self, transaction, subtransaction=False):
        """Begin commit of a transaction, starting the two-phase commit.
        """
        pass

    def tpc_abort(self, transaction):
        """Abort a transaction.
        """
        # useful for unit testing
        self._transaction_aborted = True

    def tpc_finish(self, transaction):
        """Indicate confirmation that the transaction is done.
        """
        # transaction was successfully finished
        # moving mails from transaction queue to persistent queue
        if self._transaction_aborted:
            return
        if self._transaction_voted:
            global mailQueue
            mailQueue._fastQueue(self.values())
            self._queue = {}

    def tpc_vote(self, transaction):
        """Verify that a data manager can commit the transaction
        """
        self._transaction_voted = True

    def commit(self, object, transaction):
        """CCCommit changes to an object
        """
        # payload is in tpc_finish
        pass

    def abort(self, object, transaction):
        """Abort changes to an object
        """
        # XXX clean queue just to be sure
        self._transaction_aborted = True
        self._queue = {}

    def sortKey(self):
        """Return a key to use for ordering registered DataManagers
        
        Sort order isn't important. Returning 1 is fine
        """
        return 1

def enqueueMail(mail):
    """Adds a mail to the transactional queue
    """
    transaction = get_transaction()
    queue = None
    # try to find a mail queue in the list of data managers
    for dm in transaction._objects:
        if IMailQueue.isImplementedBy(dm):
            queue = dm
            break
    # create and register a new one if no mail queue is registered
    if queue is None:
        queue = TransactionalMailQueue()
        transaction.register(queue)
    # add mail to queue
    queue.queue(mail)
