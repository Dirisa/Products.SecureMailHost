"""
"""
import os, sys
import threading
import time
import smtplib
import anydbm
from smtplib import SMTP
import socket
import cPickle as pickle
from types import IntType
import traceback

from Globals import INSTANCE_HOME
from zLOG import LOG, INFO, PROBLEM

WAIT_TIME = 10
MAX_ERRORS = 5
TEMP_ERRORS = (smtplib.SMTPConnectError, )
# XXX MAX_UID_LOOP = 10000
DB_FILE = os.path.join(INSTANCE_HOME, 'var', 'securemail_queue.db')

def sendmail(mail):
    """Sends an email
    """
    mfrom, mto, message = mail.getMail()
    # server settings
    host     = mail.getServer('host')
    port     = mail.getServer('port')
    userid   = mail.getServer('userid')
    password = mail.getServer('password')
    print userid, password
    
    # connect
    smtpserver = SMTP(host, port)
    #if debug:
    #    smtpserver.set_debuglevel(1)
    smtpserver.ehlo()
    if smtpserver.has_extn('starttls'):
        smtpserver.starttls()
        smtpserver.ehlo()
    if smtpserver.does_esmtp:
        if userid:
            smtpserver.login(userid, password)
        else:
            if userid:  #indicate error here to prevent inadvertent use of spam relay
                raise MailHostError,"Host does NOT support ESMTP, but username/password provided"
    smtpserver.sendmail(mfrom, mto, message)
    smtpserver.quit()

class Mail:
    """A email object which knows how to send itself
    """

    def __init__(self, mfrom, mto, message, server):
        """
        """
        self.mfrom = mfrom
        self.mto = mto
        self.message = message
        assert(server.get('host', None))
        assert(server.get('port', None))
        self.server = server
        self.errors = 0
        self.id = None
        
    def setId(self, id):
        """Set the unique id of the email
        """
        self.id = id
        
    def getId(self):
        """Get unique id
        """
        return self.id
    
    def incError(self):
        """Increase the error counter
        """
        self.errors+=1

    def getErrors(self):
        """Get the error counter
        """
        return self.errors
        
    def getMail(self):
        """Get email for sending
        
        (mfrom, mto, mailbody)
        """
        return (self.mfrom, self.mto, self.message)
    
    def getServer(self, key, default=None):
        """Get server configuration for sending
        
        host, port
        optional: userid, pass 
        """
        return self.server.get(key, default)

class MailStorage:
    """Stores Email objects in a queue.
    
    For safty reasons the emails are pickled on the file system in a seperate db
    to recover them after a zope crash or shutdown.
    
    put(email)          - adds an email to the queue
    get(id)             - gets an email from the queue by id
    remove(email_or_id) - removes an email from the queue
    
    To increase the performance the unpickled emails are cached in a pickle
    cache.
    """

    def __init__(self):
        if not os.path.isfile(DB_FILE):
            db = anydbm.open(DB_FILE, 'c')
            db.close()
        self.queue = anydbm.open(DB_FILE, 'w') # write
        self.lock = threading.Lock()
        self.pickle_cache = {}
    
    def send(self, mail):
        """Sends an email to the queue
        """
        id = self.mkID()
        mail.setId(id)
        try:
            self.lock.acquire()
            # store mail in pickle cache
            self.pickle_cache[id] = mail
            # store mail in queue
            dump = pickle.dumps(mail)
            self.queue[id] = dump
            self.sync()
        finally:
            self.lock.release()
        
    def get(self, id):
        """Get a mail by id
        """
        try:
            self.lock.acquire()
            if id not in self.queue:
                raise KeyError, id
            mail = self.pickle_cache.get(id, None)
            if not mail:
                dump = self.queue[id]
                mail = pickle.loads(dump)
                self.pickle_cache[id] = mail
            return mail
        finally:
            self.lock.release()

    def remove(self, mail_or_id):
        """Removes an email from the queue
        """
        if type(mail_or_id) is IntType:
            id = mail_or_id
        else:
            id = mail_or_id.getId()
        try:
            self.lock.acquire()
            del self.queue[id]
            try:
                del self.pickle_cache[id]
            except KeyError:
                pass
            self.sync()
        finally:
            self.lock.release()
   
    def sync(self):
        """syncs the DB in the fs
        
        MUST be called within an acquired lock!
        """
        sync = getattr(self.queue, 'sync', None)
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
            if id not in self.queue:
                break
            else:
                count+=1
        return id
    
    def list(self):
        """
        """
        return self.queue.keys()
    

mailQueue = MailStorage()

class MailerThread(threading.Thread):
    """The worker thread
    """
    
    def __init__(self):
        threading.Thread.__init__(self, name='asyncmail')
        self.event = threading.Event()
        self.running = True
        
    def stop(self):
        """Stop the thread
        
        Required for unit tests
        """
        LOG('SecureMailHost', INFO, 'Stopping mailer thread')
        if not self.running:
            self.running = False
            self.event.set()
        
    def run(self):
        """Main runner
        """
        # XXX
        # wrapped because of some strange problems with threading and zope
        try:
            self.run2()
        except:
            pass
    
    def run2(self):
        """
        """
        global mailQueue
        while True:
            if not self.running:
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
                    sendmail(mail)
                except TEMP_ERRORS:
                    # XXX log
                    LOG('SecureMailHost', PROBLEM, 'Temp error %s' %
                        ''.join(traceback.format_tb(sys.exc_traceback))
                    )
                except:
                    LOG('SecureMailHost', PROBLEM, 'Fatal error %s' %
                        ''.join(traceback.format_tb(sys.exc_traceback))
                    )
                    mail.incError()
                else:
                    mailQueue.remove(mail)
            else:
                # queue currently empty - waiting
                self.event.wait(WAIT_TIME)


mailThread = MailerThread()
mailThread.setDaemon(True)

# start thread
def initialize(context):
    LOG('SecureMailHost', INFO, 'Starting mailer thread')
    mailThread.start()
