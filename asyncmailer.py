"""
"""
from config import WAIT_TIME, MAX_ERRORS, TEMP_ERRORS

import sys
import traceback

from zLOG import LOG, INFO, PROBLEM

from workerthread import WorkerThread
from mailqueue import mailQueue

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
