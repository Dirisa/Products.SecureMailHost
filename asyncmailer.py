"""
"""
from config import WAIT_TIME, MAX_ERRORS, TEMP_ERRORS, DB_FILE

import os, sys
import threading
import time
import anydbm
import socket
import cPickle as pickle
from types import IntType
import traceback

from zLOG import LOG, INFO, PROBLEM


class MailStorage:
    """Stores Email objects in a queue.
    
    For safty reasons the emails are pickled on the file system in a seperate db
    to recover them after a zope crash or shutdown.
    
    queue(email)        - adds an email to the queue
    get(id)             - gets an email from the queue by id
    remove(email_or_id) - removes an email from the queue
    
    To increase the performance the unpickled emails are cached in a pickle
    cache.
    """

    def __init__(self):
        if not os.path.isfile(DB_FILE):
            db = anydbm.open(DB_FILE, 'c')
            db.close()
        self._queue = anydbm.open(DB_FILE, 'w') # write
        self._lock = threading.Lock()
        self._pickle_cache = {}
    
    def queue(self, mail):
        """Sends an email to the queue
        """
        id = self.mkID()
        mail.setId(id)
        try:
            self._lock.acquire()
            # store mail in pickle cache
            self._pickle_cache[id] = mail
            # store mail in queue
            dump = pickle.dumps(mail)
            self._queue[id] = dump
            self.sync()
        finally:
            self._lock.release()
        
    def get(self, id):
        """Get a mail by id
        """
        try:
            self._lock.acquire()
            if id not in self._queue:
                raise KeyError, id
            mail = self._pickle_cache.get(id, None)
            if not mail:
                dump = self._queue[id]
                mail = pickle.loads(dump)
                self._pickle_cache[id] = mail
            return mail
        finally:
            self._lock.release()

    def remove(self, mail_or_id):
        """Removes an email from the queue
        """
        if type(mail_or_id) is IntType:
            id = mail_or_id
        else:
            id = mail_or_id.getId()
        try:
            self._lock.acquire()
            del self._queue[id]
            try:
                del self._pickle_cache[id]
            except KeyError:
                pass
            self.sync()
        finally:
            self._lock.release()
   
    def sync(self):
        """syncs the DB in the fs
        
        MUST be called within an acquired lock!
        """
        sync = getattr(self._queue, 'sync', None)
        if sync:
            sync()
    
    def mkID(self):
        """Generates a id
        """
        host = socket.gethostname()
        count = 0
        while True:
            ts = time.time()
            id = '%s-%s-%i' % (ts, host, count)
            if id not in self._queue:
                break
            else:
                count+=1
        return id
    
    def list(self):
        """
        """
        return self._queue.keys()
    

mailQueue = MailStorage()

class MailerThread(threading.Thread):
    """The worker thread
    """
    
    def __init__(self):
        threading.Thread.__init__(self, name='asyncmail')
        self._event = threading.Event()
        self._running = True
        
    def stop(self):
        """Stop the thread
        
        Required for unit tests
        """
        LOG('SecureMailHost', INFO, 'Stopping mailer thread')
        if not self._running:
            self._running = False
            self._event.set()
        
    def run(self):
        """Main runner
        """
        # XXX
        # wrapped because of some strange problems with threading and zope
        #try:
        self.run2()
        #except:
        #    pass
    
    def run2(self):
        """
        """
        global mailQueue
        while True:
            if not self._running:
                return

            LOG('SecureMailHost', INFO, 'threading')

            for id in mailQueue.list():
                mail = mailQueue.get(id)
                # checking for max errors
                if mail.getErrors() > MAX_ERRORS:
                    LOG('SecureMailHost', PROBLEM, 'Max errors')
                    mailQueue.remove(mail)
                    continue
                # trying to send
                try:
                    mail.send()
                except TEMP_ERRORS, msg:
                    # XXX log
                    LOG('SecureMailHost', PROBLEM, 'Temp error %s\n%s' %
                        (msg, ''.join(traceback.format_tb(sys.exc_traceback)))
                    )
                except Exception, msg:
                    LOG('SecureMailHost', PROBLEM, 'Fatal error %s\n%s' %
                        (msg, ''.join(traceback.format_tb(sys.exc_traceback)))
                    )
                    mail.incError()
                else:
                    mailQueue.remove(mail)
            else:
                # queue currently empty - waiting
                self._event.wait(WAIT_TIME)


mailThread = MailerThread()
mailThread.setDaemon(True)

# start thread
def initialize(context):
    LOG('SecureMailHost', INFO, 'Starting mailer thread')
    mailThread.start()
