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

from config import WAIT_TIME, MAX_ERRORS, TEMP_ERRORS

import sys
import traceback

from zLOG import LOG, INFO, PROBLEM, DEBUG

from workerthread import WorkerThread
from mailqueue import mailQueue

class MailerThread(WorkerThread):
    """Mailer thread
    """
    
    def main(self):
        """Worker method
        """
        global mailQueue
        LOG('SecureMailHost', DEBUG, 
            'Awaking thread with %d mails left in the queue.' % len(mailQueue))

        for id in mailQueue.list():
            mail = mailQueue.get(id)
            # checking for max errors
            if mail.getErrors() > MAX_ERRORS:
                LOG('SecureMailHost', PROBLEM, 'Max errors for mail %s. '
                    'Canceling delivery!' % mail.info())
                del mailQueue[id]
                continue
            # trying to send
            try:
                mail.send()
            except TEMP_ERRORS, msg:
                LOG('SecureMailHost', PROBLEM, 'Temp error %s sending %s:\n%s' %
                    (msg, mail.info(), ''.join(traceback.format_tb(sys.exc_traceback)))
                )
            except Exception, msg:
                LOG('SecureMailHost', PROBLEM, 'Fatal error %s sending %s:\n%s' %
                    (msg, mail.info(), ''.join(traceback.format_tb(sys.exc_traceback)))
                )
                mail.incError()
            else:
                LOG('SecureMailHost', INFO, 'Mail sended: %s' % mail.info())
                del mailQueue[id]

    def stop(self):
        LOG('SecureMailHost', INFO, 'Stopping mailer thread')
        WorkerThread.stop(self)

mailThread = None

# start thread
def initializeMailThread():
    global mailThread
    if not mailThread:
        LOG('SecureMailHost', INFO, 'Starting mailer thread')
        mailThread = MailerThread(name='asyncmail', wait=WAIT_TIME)
        mailThread.start()

__all__ = ('mailThread', 'mailQueue', 'initializeMailThread', )
