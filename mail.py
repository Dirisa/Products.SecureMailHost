"""
"""
from config import X_MAILER

import os, sys
import smtplib
import email.Message
import socket
from DateTime import DateTime
from random import randint

from zLOG import LOG, INFO, PROBLEM
from Products.MailHost.MailHost import MailHostError

class Mail:
    """A email object which knows how to send itself
    
    mfrom     - mail from tag (only for SMTP server)
    mto       - mail to tag (only for SMTP server)
    message   - The message email.Message.Message based object
    smtp_host - SMTP server address
    smtp_host - SMTP server port
    **kwargs  - additional keywords like userid, password and forceTLS
    """

    def __init__(self, mfrom, mto, message, 
                 smtp_host='localhost', smtp_port=25,
                 **kwargs):
        self.mfrom = mfrom
        self.mto = mto
        # message must be email.Message.Message based
        assert(isinstance(message, email.Message.Message))
        # Add some import headers
        if not message.has_key('Date'):
            message['Date'] = DateTime().rfc822()
        if not message.has_key('X-Mailer'):
            message['X-Mailer'] = X_MAILER
        if not message.has_key('Message-Id'):
            date = DateTime().strftime('%Y%m%d%H%M%S')
            rand = randint(100000, 999999)
            host = socket.gethostname()
            message['Message-Id'] = '<%s.%d@%s>' % (date, rand, host)

        self.message = message
        
        self.host = smtp_host
        self.port = int(smtp_port)

        self.kwargs = kwargs
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

    def send(self, debug=False):
        """Send email to the SMTP server
        """
        kw = self.kwargs
        userid   = kw.get('userid', None)
        password = kw.get('password', None)
        forceTLS = kw.get('forctls', False)
        message  = self.message.as_string()
        
        # connect
        smtpserver = smtplib.SMTP(self.host, self.port)
        if debug:
            smtpserver.set_debuglevel(1)
        smtpserver.ehlo()
        # check for ssl encryption
        if smtpserver.has_extn('starttls'):
            smtpserver.starttls()
            smtpserver.ehlo()
        elif forceTLS:
            raise MailHostError, 'Host does NOT support StartTLS but it is required'
        # login
        if smtpserver.does_esmtp:
            if userid:
                smtpserver.login(userid, password)
        elif userid:
            #indicate error here to prevent inadvertent use of spam relay
            raise MailHostError, 'Host does NOT support ESMTP, but username/password provided'
        # send and quiet
        smtpserver.sendmail(self.mfrom, self.mto, message)
        smtpserver.quit()
