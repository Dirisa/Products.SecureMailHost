"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: notifications.py,v 1.42 2004/07/13 18:28:27 ajung Exp $
"""

import sys
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.Header import Header
import email.Utils 

from zLOG import LOG, ERROR, INFO
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

import util, notification_policies

def notify(issue):
    """ notification handling """

    collector = issue._getCollector()
    NP = eval('notification_policies.%s(issue)' % collector.getNotification_policy())
    recipients = NP.getRecipients()
    recipients = enrich_recipients(issue, recipients)
    send_notifications(recipients, issue)
    

def enrich_recipients(issue, recipients):
    """ take the recipients dict. and try to add as much as possible
        additional user data that we can collector from our env.
    """

    r = recipients
    membership = getToolByName(issue, 'portal_membership', None)

    # add current user (might be a non-assigned supporter performing 
    # an issue followup)
    username = getSecurityManager().getUser().getUserName()
    if username != 'Anonymous User':
        r[username] = {}        

    for uid, u_dict in r.items():
        member = membership.getMemberById(uid)
        if member:
            r[uid]['send_attachments'] = util.safeGetProperty(member, 'pcng_send_attachments', 'no') or 'no'
            r[uid]['send_emails'] = util.safeGetProperty(member, 'pcng_send_emails', 'yes') or 'no'
            if not u_dict.has_key('email'):    # guess email
                r[uid]['email'] = util.safeGetProperty(member, 'email', '') or ''
    return r


def latest_upload(issue):
    """ return the latest uploaded object """
    objs = list(issue.objectValues())
    objs.sort(lambda x,y: cmp(x.bobobase_modification_time(), y.bobobase_modification_time()))
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

    encoding = 'utf8'
    collector = issue._getCollector()
    dest_emails = [ v['email'] for v in recipients.values()     
                               if util.isValidEmailAddress(v.get('email','')) and
                                  v.get('send_emails','yes').lower() == 'yes']
    dest_emails = util.remove_dupes(dest_emails)
    # No recipients? Don't send notifications for half-filled issues!
    if not dest_emails or not issue.isPersistent(): return  

    outer = MIMEMultipart()
    outer['From'] = collector.getCollector_email()
    outer['To'] = ','.join(dest_emails)
    subject = '[%s/%s]  %s (#%s/%s)' %  (str(collector.getCollector_abbreviation()), issue.getId(), 
              issue.Title(), len(issue), issue.Translate(issue.lastAction(),issue.lastAction()))
    outer['Subject'] = Header(subject, encoding)
    outer['Message-ID'] = email.Utils.make_msgid()
    outer['Reply-To'] = collector.getCollector_email()
    body = issue.format_transcript(collector.getNotification_language())
    outer['Content-Type'] = 'text/plain; charset=%s' % encoding
    outer.attach(MIMEText(body.encode('utf-8'), _charset='utf-8'))
            
    if send_attachments and  issue.lastAction() == 'Upload':
        # we need to attach the latest Upload to the email
        obj = latest_upload(issue)
        if obj.meta_type in('Portal Image',):
            att = MIMEImage(str(obj.data))
            att.add_header('content-disposition', "attachment; filename=%s" % obj.getId())
            outer.attach(att)

    # Keyfile
    if issue.getIssue_email_verification() != 'disabled':
        encoded_text = issue.encode_information(issue.absolute_url(1))
        keyfile = MIMEText(encoded_text)
        keyfile.add_header('content-type', 'text/plain')
        keyfile.add_header('content-disposition', "attachment; filename=pcng.key")
        outer.attach(keyfile)

    if hasattr(collector, 'MailHost'):
        MH = getattr(collector, 'MailHost') 
        
        try:
            LOG('plongcollectorng', INFO, 'recipients for %s: %s' % (issue.absolute_url(1), dest_emails))
            MH._send(collector.collector_email, dest_emails, outer.as_string())
        except: 
            LOG('plonecollectorng', ERROR, 'MailHost.send() failed', error=sys.exc_info())
    else:
        LOG('plonecollectorng', ERROR, 'MailHost not found')

