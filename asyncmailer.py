"""
"""
from config import WAIT_TIME, MAX_ERRORS, TEMP_ERRORS

import sys
import threading
import traceback
from mailqueue import mailQueue

from zLOG import LOG, INFO, PROBLEM


class WorkerThread(threading.Thread):
    """Common Worker Thread
    
    worker = WorkerThread(name='name', wait=float(10))
    worker.setDaemon(True)
    worker.start()
    # calling main() method every 10 seconds until stopped
    worker.stop() # stopped
    worker.start() # started again
    """
    
    def __init__(self, name='WorkerThread', wait=10.0):
        threading.Thread.__init__(self, name=name)
        self._event = threading.Event() # event handler to time the loop
        self._running = False           # thread is stop until calling start
        self._wait = float(wait)
        
    def start(self):
        """Start the thread
        """
        self._running = True
        self._event.clear() # enable event timer
        threading.Thread.start(self)
        
    def run(self):
        """Infinitive loop
        """
        while True:
            if not self._running:
                return
            self.main()
            self._event.wait(self._wait)

    def main(self):
        """Worker method
        """
        print 'Does nothing'

    def stop(self):
        """Stop the thread
        
        Required for unit tests
        """
        if not self._running:
            self._running = False
            self._event.set()

class MailerThread(WorkerThread):
    """Mailer thread
    """
    
    def run(self):
        """Infinitive loop
        """
        # XXX
        # Wrapped because of some strange problems with threading and zope
        # After SIGTERM or SIGINT the thread can terminated without throwing
        # a nasty error message
        try:
            WorkerThread.run(self)
        except:
            pass
    
    def main(self):
        """Worker method
        """
        global mailQueue
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

    def stop(self):
        LOG('SecureMailHost', INFO, 'Stopping mailer thread')
        WorkerThread.stop(self)

mailThread = MailerThread(name='asyncmail', wait=WAIT_TIME)
mailThread.setDaemon(True)

# start thread
def initialize(context):
    LOG('SecureMailHost', INFO, 'Starting mailer thread')
    mailThread.start()
