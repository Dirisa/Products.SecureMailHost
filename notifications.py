"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: notifications.py,v 1.6 2003/10/11 20:46:49 ajung Exp $
"""

import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.Header import Header
import email.Utils 

from zLOG import LOG, ERROR
from Products.CMFCore.utils import getToolByName

import util

def notify(issue):
    """ notification handling """

    collector = issue._getCollector()
    if collector.email_notifications == 'none': return

    recipients = recipients4issue(issue)
    recipients = enrich_recipients(issue, recipients)
    send_notifications(recipients, issue)
    

def recipients4issue(issue):
    """ determine the list of recipients for this issue """

    collector = issue._getCollector()
    r = {'submitter' : {'email': issue.contact_email}}
    for uid in collector._managers: r[uid] = {}   # all managers

    if collector.email_notifications == 'assigned':
        for uid in issue.assigned_to(): r[uid] = {} # all assignees       
    else:
        for uid in collector._supporters: r[uid] = {} # all supporters

    # TODO: support for substitutes
    # TODO: support for confidential workflow
    # TODO: support for watchers

    return r


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

    outer = MIMEMultipart()
    outer['From'] = collector.collector_email 
    outer['To'] = ','.join(dest_emails)
    subject = '[%s] #%s: %s' %  (collector.getId(), issue.getId(),  issue.Title())
    subject = str(Header(subject, 'iso-8859-1'))
    outer['Subject'] = subject
    outer['Message-ID'] = email.Utils.make_msgid()
    outer['Reply-To'] = collector.collector_email
    body, encoding =  eval('issue.%s()' % collector.issue_formatter)   # skin method
    outer['Content-Type'] = 'text/plain; charset=%s' % encoding
    outer.attach(MIMEText(body, _charset=encoding))

    mh = getattr(collector, 'MailHost') 
    
    try:
        mh._send(collector.collector_email, dest_emails, outer.as_string())
    except: 
        LOG('PloneCollectorNG', ERROR, 'MailHost.send() failed', error=sys.exc_info())

