"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: notifications.py,v 1.14 2003/11/01 17:03:25 ajung Exp $
"""

import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.Header import Header
import email.Utils 

from zLOG import LOG, ERROR, TRACE
from Products.CMFCore.utils import getToolByName

import util, notification_policies

def notify(issue):
    """ notification handling """

    collector = issue._getCollector()

    NP = eval('notification_policies.%s(issue)' % collector.notification_policy)
    recipients = NP.getRecipients()
    recipients = enrich_recipients(issue, recipients)
    send_notifications(recipients, issue)
    

def enrich_recipients(issue, recipients):
    """ take the recipients dict. and try to add as much as possible
        additional user data that we can collector from our env.
    """

    r = recipients
    membership = getToolByName(issue, 'portal_membership', None)

    for uid, u_dict in r.items():
        member = membership.getMemberById(uid)
        if member:
            r[uid]['send_attachments'] = util.safeGetProperty(member, 'pcng_send_attachments', 'no')
            if not u_dict.has_key('email'):    # guess email
                r[uid]['email'] = util.safeGetProperty(member, 'email', '')
    return r


def latest_upload(issue):
    """ return the latest uploaded object """
    objs = issue.objectValues()
    objs.sort(lambda x,y: cmp(x.bobobase_modification_time, y.bobobase_modification_time))
    return objs[0]


def divide_recipients(recipients):
    """ Divide the recipients dict into a dict with
        recipients that receive attachements and recipients
        that do not receive attachements. We return a tuple
        of dicts with recipients (recipient_with_attachments,
        recipients_without_attachement)
    """

    r_with = {}; r_without = {}
    for k,v in recipients.items():
        if v.get('send_attachments', None) in ('yes', 'YES'):
            r_with[k] = v
        else:
            r_without[k] = v
    return (r_with, r_without)


def send_notifications(recipients, issue):
    """ send out notifications through email """

    r_with, r_without = divide_recipients(recipients)
    _send_notifications(r_without, issue, send_attachments=0)
    _send_notifications(r_with, issue, send_attachments=1)


def _send_notifications(recipients, issue, send_attachments=0):
    """ create the notification emails """

    collector = issue._getCollector()

    dest_emails = [ v['email'] for v in recipients.values() if util.isValidEmailAddress(v.get('email','')) ]
    if not dest_emails: return  # No recipients???

    outer = MIMEMultipart()
    outer['From'] = collector.collector_email 
    outer['To'] = ','.join(dest_emails)
    subject = '[%s] %s/%s %s "%s"' %  (collector.collector_abbreviation, issue.getId(), len(issue), issue._last_action, issue.Title())
    subject = str(Header(subject, 'iso-8859-1'))
    outer['Subject'] = subject
    outer['Message-ID'] = email.Utils.make_msgid()
    outer['Reply-To'] = collector.collector_email
    body, encoding =  eval('issue.%s()' % collector.issue_formatter)   # skin method
    outer['Content-Type'] = 'text/plain; charset=%s' % encoding
    outer.attach(MIMEText(body, _charset=encoding))

    if send_attachments and  issue.lastAction() == 'Upload':
        # we need to attach the latest Upload to the email
        obj = latest_upload(issue)
        if obj.meta_type in('Portal Image',):
            outer.attach(MIMEImage(str(obj.data))) 
        
    MH = getattr(collector, 'MailHost') 
    
    try:
        LOG('plongcollectorng', TRACE, 'recipients: %s' % dest_emails)
        MH._send(collector.collector_email, dest_emails, outer.as_string())
    except: 
        LOG('plonecollectorng', ERROR, 'MailHost.send() failed', error=sys.exc_info())

