"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: notifications.py,v 1.10 2003/10/14 15:20:32 ajung Exp $
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
        if not u_dict.has_key('email'):    # guess email
        
            member = membership.getMemberById(uid)
            r[uid]['email'] = util.safeGetProperty(member, "email", "")

    return r


def send_notifications(recipients, issue):
    """ send out notifications through email """

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

    mh = getattr(collector, 'MailHost') 
    
    try:
        LOG('plongcollector', TRACE, 'recipients: %s' % dest_emails)
        mh._send(collector.collector_email, dest_emails, outer.as_string())
    except: 
        LOG('PloneCollectorNG', ERROR, 'MailHost.send() failed', error=sys.exc_info())

