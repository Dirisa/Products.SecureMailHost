from config import BAD_HEADERS
from copy import deepcopy

import email.Message
import email.Header
import email.MIMEText
import email
from email.Utils import getaddresses
from email.Utils import formataddr

import re

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import use_mailhost_services
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Persistence import Persistent
from Products.MailHost.MailHost import MailHostError, MailBase
from Products.SecureMailHost.mail import Mail

class SMTPError(Exception):
    pass

EMAIL_RE = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,63}|([0-9]{1,3}\.){3}[0-9]{1,3})$", re.IGNORECASE)
# used to find double new line (in any variant)
EMAIL_CUTOFF_RE = re.compile(r".*[\n\r][\n\r]")

# We need to encode usernames in email addresses.
# This is especially important for Chinese and other languanges.
# Sample email addresses:
#
# aaa<a@b.c>, "a,db"<a@b.c>, apn@zopechina.com, "ff s" <a@b.c>, asdf<a@zopechina.com>
EMAIL_ADDRESSES_RE = re.compile(r'(".*?" *|[^,^"^>]+?)(<.*?>)')

class MailAddressTransformer:
    """ a transformer for substitution """
    def __init__(self, charset):
        self.charset = charset

    def __call__(self, matchobj):
        name = matchobj.group(1)
        address = matchobj.group(2)
        return str(email.Header.Header(name, self.charset)) + address

def encodeHeaderAddress(address, charset):
    """ address encoder """
    return address and \
      EMAIL_ADDRESSES_RE.sub(MailAddressTransformer(charset), address)

def formataddresses(fieldvalues):
    """Takes a list of (REALNAME, EMAIL) and returns one string
    suitable for To or CC
    """
    return ', '.join([formataddr(pair) for pair in fieldvalues])

manage_addMailHostForm = DTMLFile('www/addMailHost_form', globals())
def manage_addMailHost(self, id, title='', smtp_host='localhost',
                       smtp_port=25, smtp_userid=None,
                       smtp_pass=None, smtp_notls=None, REQUEST=None):
    """Add a MailHost
    """
    ob = SecureMailHost(id, title, smtp_host, smtp_port,
                        smtp_uid=smtp_userid, smtp_pwd=smtp_pass,
                        smtp_notls=smtp_notls)
    self._setObject(id, ob)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

add = manage_addMailHost

class SecureMailBase(MailBase):
    """A more secure mailhost with ESMTP features and header checking
    """
    meta_type = 'Secure Mail Host'
    security = ClassSecurityInfo()

    # BBB for old names, prefer the names from MailHost

    def get_smtp_userid(self):
        return self.smtp_uid

    def set_smtp_userid(self, value):
        self.smtp_uid = value

    smtp_userid = property(get_smtp_userid, set_smtp_userid)

    def get_smtp_pass(self):
        return self.smtp_pwd

    def set_smtp_pass(self, value):
        self.smtp_pwd = value

    smtp_pass = property(get_smtp_pass, set_smtp_pass)

    def get_smtp_notls(self):
        return not self.force_tls

    def set_smtp_notls(self, value):
        self.force_tls = not value

    smtp_notls = property(get_smtp_notls, set_smtp_notls)

    def __init__(self, id='', title='', smtp_host='localhost', smtp_port=25,
                 force_tls=False, smtp_uid='', smtp_pwd='', smtp_queue=False,
                 smtp_queue_directory='/tmp',
                 smtp_notls=None, smtp_userid=None, smtp_pass=None):
        # BBB for old init arguments
        if smtp_userid is not None:
            smtp_uid = smtp_userid
        if smtp_pass is not None:
            smtp_pwd = smtp_pass
        if smtp_notls is not None:
            force_tls = not smtp_notls
        MailBase.__init__(self, id=id, title=title, smtp_host=smtp_host,
                          smtp_port=smtp_port, force_tls=force_tls,
                          smtp_uid=smtp_uid, smtp_pwd=smtp_pwd,
                          smtp_queue=smtp_queue,
                          smtp_queue_directory=smtp_queue_directory)

    security.declareProtected(use_mailhost_services, 'secureSend')
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
            Content subtype of the email e.g. 'plain' for text/plain (ignored
            if message is a email.Message.Message instance)
        charset:
            Charset used for the email, subject and email addresses
        kwargs:
            Additional headers
        """
        mto  = self.emailListToString(mto)
        mcc  = self.emailListToString(mcc)
        mbcc = self.emailListToString(mbcc)
        # validate email addresses
        # XXX check Return-Path
        for addr in mto, mcc, mbcc:
            if addr:
                result = self.validateEmailAddresses(addr)
                if not result:
                    raise MailHostError, 'Invalid email address: %s' % addr
        result = self.validateSingleEmailAddress(mfrom)
        if not result:
            raise MailHostError, 'Invalid email address: %s' % mfrom

        # create message
        if isinstance(message, email.Message.Message):
            # got an email message. Make a deepcopy because we don't want to
            # change the message
            msg = deepcopy(message)
        else:
            if isinstance(message, unicode):
                message = message.encode(charset)
            msg = email.MIMEText.MIMEText(message, subtype, charset)

        mfrom = encodeHeaderAddress(mfrom, charset)
        mto = encodeHeaderAddress(mto, charset)
        mcc = encodeHeaderAddress(mcc, charset)
        mbcc = encodeHeaderAddress(mbcc, charset)

        # set important headers
        self.setHeaderOf(msg, skipEmpty=True, From=mfrom, To=mto,
                 Subject=str(email.Header.Header(subject, charset)),
                 Cc=mcc, Bcc=mbcc)

        for bad in BAD_HEADERS:
            if bad in kwargs:
                raise MailHostError, 'Header %s is forbidden' % bad
        self.setHeaderOf(msg, **kwargs)

        # we have to pass *all* recipient email addresses to the
        # send method because the smtp server doesn't add CC and BCC to
        # the list of recipients
        to = msg.get_all('to', [])
        cc = msg.get_all('cc', [])
        bcc = msg.get_all('bcc', [])
        recipient_list = getaddresses(to + cc + bcc)
        all_recipients = [formataddr(pair) for pair in recipient_list]

        # finally send email
        return self._send(mfrom, all_recipients, msg, debug=debug)

    security.declarePrivate('setHeaderOf')
    def setHeaderOf(self, msg, skipEmpty=False, **kwargs):
        """Set the headers of the email.Message based instance

        All occurences of the key are deleted first!
        """
        for key, val in kwargs.items():
            del msg[key] # save - email.Message won't raise a KeyError
            if skipEmpty and not val:
                continue
            msg[key] = val
        return msg

    security.declarePrivate('_send')
    def _send(self, mfrom, mto, messageText, debug=False):
        """Send the message
        """
        if debug:
            if not isinstance(messageText, email.Message.Message):
                message = email.message_from_string(messageText)
            else:
                message = messageText
            return Mail(mfrom, mto, message, smtp_host=self.smtp_host,
                        smtp_port=self.smtp_port, userid=self.smtp_uid,
                        password=self.smtp_pwd, notls=self.smtp_notls
                       )

        if isinstance(messageText, email.Message.Message):
            messageText = messageText.as_string()
        MailBase._send(self, mfrom, mto, messageText)

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
        if not isinstance(addr_list, (list, tuple)):
            # a string is supposed to be a valid list of email addresses
            # or None
            return addr_list
        # stage 2: get a list of address strings using email.formataddr
        addresses = []
        for addr in addr_list:
            if isinstance(addr, basestring):
                addresses.append(email.Utils.formataddr(('', addr)))
            else:
                if len(addr) != 2:
                    raise ValueError(
                        "Wrong format: ('name', 'email') is required")
                addresses.append(email.Utils.formataddr(addr))
        # stage 3: return the addresses as comma seperated string
        return ', '.join(addresses)

    ######################################################################
    # copied from CMFPlone 2.0.2 PloneTool.py

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email
        address, see validateEmailAddress
        """
        if not isinstance(address, basestring):
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
        if not isinstance(address, basestring):
            return False

        sub = EMAIL_CUTOFF_RE.match(address);
        if sub != None:
            # Address contains two newlines (spammer attack using
            # "address\n\nSpam message")
            return False

        if len(getaddresses([address])) != 1:
            # none or more than one address
            return False

        # Validate the address
        for name,addr in getaddresses([address]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see
        also validateSingleEmailAddress
        """
        if not isinstance(addresses, basestring):
            return False

        sub = EMAIL_CUTOFF_RE.match(addresses);
        if sub != None:
            # Addresses contains two newlines (spammer attack using
            # "To: list\n\nSpam message")
            return False

        # Validate each address
        for name,addr in getaddresses([addresses]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    # copied from CMFPlone 2.0.2 PloneTool.py
    ######################################################################


InitializeClass(SecureMailBase)

class SecureMailHost(Persistent, SecureMailBase):
    "persistent version"
