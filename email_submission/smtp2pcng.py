#!/usr/local/bin/python2.1

"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: smtp2pcng.py,v 1.1 2004/02/25 18:01:05 ajung Exp $
"""

import sys, os, logging
import email, email.Iterators
from email.Header import decode_header 
from email.MIMEText import MIMEText

class Result:

    def __init__(self):
        self.attachments = []

    def addAttachment(self, data, mimetype, filename):
        self.attachments.append( (data, mimetype, filename))

    def getAttachments(self):
        return self.attachments


def parse_mail():

    text = sys.stdin.read()
    msg = email.message_from_string(text)

    R = Result()

    for part in msg.walk():
        ct = part.get_content_type() 

        if part.has_key("From"):
            R.from_addr = R.reply_to = email.Utils.parseaddr(part.get("From"))

        if part.has_key("Reply-To"):
            R.reply_to = email.Utils.parseaddr(part.get("Reply-To"))[1]

        if part.has_key("Subject"):
            R.subject = decode_header(part.get("Subject"))[0][0]

        if ct in ('text/plain',):
            R.body = part.get_payload(decode=1)

        elif ct.startswith('image/'):
            R.addAttachment(part.get_payload(decode=1), ct, None)

    print 'Email: %s (%s)' % (R.from_addr, R.reply_to)
    print 'Payload:\n%s\n' % R.body
    print [ (a[1],len(a[0])) for a in R.getAttachments()]
    return R

if __name__ == '__main__':
    R = parse_mail()
