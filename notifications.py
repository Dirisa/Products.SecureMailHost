"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: notifications.py,v 1.1 2003/10/11 11:30:26 ajung Exp $
"""

import sys
from zLOG import LOG, ERROR
from Products.CMFCore.utils import getToolByName
import util

def notify(issue):
    """ notification handling """

    collector = issue.aq_parent
    if collector.email_notifications == 'none': return

    recipients = recipients4issue(issue)
    recipients = enrich_recipients(issue, recipients)
    send_notifications(recipients, issue)
    

def recipients4issue(issue):
    """ determine the list of recipients for this issue """

    collector = issue.aq_parent
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

    collector = issue.aq_parent
#    email_msg = format_transcript(issue)      # TODO
    email_msg = ''
    print recipients
    dest_emails = [ v['email'] for v in recipients.values() if v.get('email','') != '']
    mh = getattr(collector, 'MailHost') 

    print dest_emails
    try:
        mh._send(collector.collector_email, dest_emails, email_msg.as_string())
    except: 
        LOG('PloneCollectorNG', ERROR, 'MailHost.send() failed', error=sys.exc_info())
