##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
###############
# 12/23/03 bowerymarc added ESMTP support
# based on v.1.74.6.6 from zope 2.6.2
# 
##############################################################################
"""SMTP mail objects
$Id: SecureMailHost.py,v 1.6 2004/05/17 12:00:28 tiran Exp $
"""

from config import BAD_HEADERS

from types import StringType, TupleType, ListType
from copy import deepcopy

import email.Message
import email.MIMEText

import re

from Globals import Persistent, DTMLFile, InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, \
                                      use_mailhost_services
from DateTime import DateTime

from Products.MailHost.MailHost import MailHostError, MailBase
class SMTPError(Exception):
    pass

from Products.SecureMailHost.mail import Mail
from Products.SecureMailHost.asyncmailer import mailQueue

EMAIL_RE = re.compile(r"^([0-9a-zA-Z_&.+-]+!)*[0-9a-zA-Z_&.+-]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$")
EMAIL_CUTOFF_RE = re.compile(r".*[\n\r][\n\r]") # used to find double new line (in any variant)

#XXX Remove this when we don't depend on python2.1 any longer, use email.Utils.getaddresses instead
from rfc822 import AddressList
def _getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) for each fieldvalue."""
    all = ', '.join(fieldvalues)
    a = AddressList(all)
    return a.addresslist


manage_addMailHostForm=DTMLFile('www/addMailHost_form', globals())
def manage_addMailHost( self, id, title='', smtp_host='localhost'
                      , smtp_port=25
                      , smtp_userid=None, smtp_pass=None
                      , REQUEST=None ):
    ' add a MailHost into the system '
    ob = SecureMailHost( id, title, smtp_host, smtp_port, smtp_userid, smtp_pass )
    self._setObject( id, ob )

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

add = manage_addMailHost

class SecureMailBase(MailBase):
    """A more secure mailhost with ESMTP features and header checking
    """

    meta_type='Secure Mail Host'
    manage=manage_main=DTMLFile('www/manageMailHost', globals())
    manage_main._setName('manage_main')
    index_html=None
    security = ClassSecurityInfo()

    def __init__( self, id, title='', smtp_host='localhost', smtp_port=25, smtp_userid='', smtp_pass='' ):
        """Initialize a new MailHost instance
        """
        self.id = id
        self.setConfiguration( title, smtp_host, smtp_port, smtp_userid, smtp_pass)

    security.declareProtected( 'Change configuration', 'manage_makeChanges' )
    def manage_makeChanges(self, title, smtp_host, smtp_port, smtp_userid, smtp_pass, REQUEST=None):
        """make the changes
        """
        self.setConfiguration(title, smtp_host, smtp_port, smtp_userid, smtp_pass)
        if REQUEST is not None:
            msg = 'MailHost %s updated' % self.id
            return self.manage_main( self
                                   , REQUEST
                                   , manage_tabs_message=msg
                                   )

    security.declarePrivate('setConfiguration')
    def setConfiguration(self, title, smtp_host, smtp_port, smtp_userid, smtp_pass):
        """Set configuration
        """
        self.title = title
        self.smtp_host = str(smtp_host)
        self.smtp_port = int(smtp_port)
        if smtp_userid:
            self._smtp_userid = smtp_userid
        else:
            self._smtp_userid = None
        if smtp_pass:
            self._smtp_pass = smtp_pass
        else:
            self._smtp_pass = None

    security.declareProtected( use_mailhost_services, 'sendTemplate' )
    def sendTemplate(trueself, self, messageTemplate,
                     statusTemplate=None, mto=None, mfrom=None,
                     encode=None, REQUEST=None):
        """render a mail template, then send it...
        """
        raise MailHostError, 'sendTemplate is disabled'

    security.declareProtected( use_mailhost_services, 'send' )
    def send(self, messageText, mto=None, mfrom=None, subject=None, 
             encode=None):
        """Send email
        """
        raise MailHostError, 'send is disabled'

    def secureSend(self, message, mto, mfrom, subject='[No Subject]',
                   mcc=None, mbcc=None, subtype='plain', charset='us-ascii',
                   debug=False, **kwargs):
        """A more secure way to send a message
            
        message:
            The plain message text without any headers or an
            email.Message.Message based instance
        mto:
            To: field (string or list)
        mfrom:
            From: field
        subject:
            Message subject (default: [No Subject])
        mcc:
            Cc: (carbon copy) field (string or list)
        mbcc:
            Bcc: (blind carbon copy) field (string or list)
        subtype:
            Content subtype of the email e.g. 'plain' for text/plain
        charset:
            Charset used for the email
        kwargs:
            Additional headers
        """
        # check email addresses
        # XXX check Return-Path
        mto  = self.emailListToString(mto)
        mcc  = self.emailListToString(mcc)
        mbcc = self.emailListToString(mbcc)
        for addr in mto, mcc, mbcc:
            if addr:
                result = self.validateEmailAddresses(addr)
                if not result:
                    raise MailHostError, 'Invalid email address: %s' % addr
        result = self.validateSingleEmailAddress(mfrom)
        if not result:
            raise MailHostError, 'Invalid email address: %s' % addr

        # create message
        if isinstance(message, email.Message.Message):
            # got an email message. Make a deepcopy because we don't want to
            # change the message
            msg = deepcopy(message)
            # XXX what about subtype and charset?
            if subtype != 'plain' or charset != 'us-ascii':
                raise MailHostError
        else:
            msg = email.MIMEText.MIMEText(message, subtype, charset)

        # set important headers
        self.setHeaderOf(msg, skipEmpty=True, From=mfrom, To=mto,
                              Subject=subject, Cc = mcc, Bcc = mbcc)

        for bad in BAD_HEADERS:
            if bad in kwargs:
                raise MailHostError, 'Header %s is forbidden' % bad
        self.setHeaderOf(msg, **kwargs)

        # finally send email
        if debug:
            return (mfrom, mto, msg)
        else:
            self._send(mfrom, mto, msg)

    def setHeaderOf(self, msg, skipEmpty=False, **kwargs):
        """Set the headers of the email.Message based instance
        
        All occurences of the key are deleted first!
        """
        for key, val in kwargs.items():
            del msg[key] # save - email.Message won't raise a KeyError
            if not val:
                continue
            msg[key] = val
        return msg

    security.declarePrivate( '_send' )
    def __SYNC_send( self, mfrom, mto, messageText, debug = False):
        """Send the message
        """
        mail = Mail(mfrom, mto, messageText,
                    smtp_host=self.smtp_host, smtp_port=self.smtp_port,
                    userid=self._smtp_userid, password=self._smtp_pass
                   )
        mail.send()

    def __ASYNC_send( self, mfrom, mto, messageText, debug = False):
        """Send the message
        """
        mail = Mail(mfrom, mto, messageText,
                    smtp_host=self.smtp_host, smtp_port=self.smtp_port,
                    userid=self._smtp_userid, password=self._smtp_pass
                   )
        mailQueue.queue(mail)

    _send = __ASYNC_send

    security.declarePublic('emailListToString')
    def emailListToString(self, addr_list):
        """Converts a list of emails to rfc822 conform data
        
        Input:
            ('email', 'email', ...)
            or
            (('name', 'email'), ('name', 'email'), ...)
            or mixed
        """
        # stage 1: test for type
        if type(addr_list) not in (TupleType, ListType):
            # a string is supposed to be a valid list of email addresses
            # or None
            return addr_list
        # stage 2: get a list of address strings using email.formataddr
        addresses = []
        for addr in addr_list:
            if type(addr) is StringType:
                addresses.append(email.Utils.formataddr(('', addr)))
            else:
                if size(addr) != 2:
                    raise ValueError, "Wrong format: ('name', 'email') is required"
                addresses.append(email.Utils.formataddr(addr))
        # stage 3: return the addresses as comma seperated string
        return ', '.join(addresses)

    ######################################################################
    # copied from CMFPlone 2.0.2 PloneTool.py

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email address, see validateEmailAddress
        """
        if type(address) is not StringType:
            return False

        sub = EMAIL_CUTOFF_RE.match(address);
        if sub != None:
            # Address contains two newlines (possible spammer relay attack)
            return False

        # sub is an empty string if the address is valid
        sub = EMAIL_RE.sub('', address)
        if sub == '':
            return True
        return False

    security.declarePublic('validateSingleEmailAddress')
    def validateSingleEmailAddress(self, address):
        """Validate a single email address, see also validateEmailAddresses
        """
        if type(address) is not StringType:
            return False
        
        sub = EMAIL_CUTOFF_RE.match(address);
        if sub != None:
            # Address contains two newlines (spammer attack using "address\n\nSpam message")
            return False
        
        if len(_getaddresses([address])) != 1:
            # none or more than one address
            return False
        
        # Validate the address
        for name,addr in _getaddresses([address]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see also validateSingleEmailAddress
        """
        if type(addresses) is not StringType:
            return False
        
        sub = EMAIL_CUTOFF_RE.match(addresses);
        if sub != None:
            # Addresses contains two newlines (spammer attack using "To: list\n\nSpam message")
            return False
        
        # Validate each address
        for name,addr in _getaddresses([addresses]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    # copied from CMFPlone 2.0.2 PloneTool.py
    ######################################################################


InitializeClass(SecureMailBase)

class SecureMailHost(Persistent, SecureMailBase):
    "persistent version"
