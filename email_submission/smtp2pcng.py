#!/usr/local/bin/python2.1

"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: smtp2pcng.py,v 1.3 2004/02/28 10:22:05 ajung Exp $
"""

import sys, os, logging, base64
import httplib, urllib, urlparse
from cStringIO import StringIO
import email, email.Iterators
from optparse import OptionParser
from email.Header import decode_header 
from email.MIMEText import MIMEText

class Result:

    def __init__(self):
        self.attachments = []

    def addAttachment(self, data, mimetype, filename):
        self.attachments.append( (data, mimetype, filename))

    def getAttachments(self):
        return self.attachments

    def toXML(self):
        IO = StringIO()
        IO.write('<?xml version="1.0" encoding="utf-8"?>\n')
        IO.write('<issue>\n')
        IO.write('<sendername>%s</sendername>\n' % self.sendername)
        IO.write('<senderaddress>%s</senderaddress>\n' % self.senderaddress)
        IO.write('<replyto>%s</replyto>\n' % self.reply_to)
        IO.write('<subject>%s</subject>\n' % self.subject)
        IO.write('<body>%s</body>\n' % self.body)

        for a in self.getAttachments():
            IO.write('<attachment mimetype="%s" filename="%s">\n' % a[1:])
            IO.write(base64.encodestring(a[0]))
            IO.write('</attachment>\n')
            
        IO.write('</issue>\n')
        return IO.getvalue()
    

def parse_mail():

    text = sys.stdin.read()
    msg = email.message_from_string(text)

    R = Result()

    for part in msg.walk():
        ct = part.get_content_type() 
        encoding = part.get_charset() or 'iso-8859-15'

        if part.has_key("From"):
            R.sendername, R.senderaddress = email.Utils.parseaddr(part.get("From"))
            R.reply_to = R.senderaddress

        if part.has_key("Reply-To"):
            R.reply_to = email.Utils.parseaddr(part.get("Reply-To"))[1]

        if part.has_key("Subject"):
            R.subject = decode_header(part.get("Subject"))[0][0]

        if ct in ('text/plain',):
            R.body = unicode(part.get_payload(decode=1), encoding).encode('utf-8')
        elif ct.startswith('image/'):
            R.addAttachment(part.get_payload(decode=1), ct, part.get_filename())

    return R

def submit_request(R, options):
    params = urllib.urlencode({'xml': R.toXML()})
    headers = {"Content-type": "application/x-www-form-urlencoded", 
               "Accept": "text/plain",
               'Authorization': 'Basic ' + base64.encodestring('%s:%s' % (options.username, options.password))[:-1],
              }
    f = urlparse.urlparse(options.url)
    conn = httplib.HTTPConnection(f[1])

    conn.request("POST", f[2], params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    conn.close()

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-u', '--url', dest='url', help='PloneCollectorNG URL to add issues')
    parser.add_option('-X', '--username', dest='username', help='Plone user name')
    parser.add_option('-P', '--password', dest='password', help='Plone user password')

    options, args = parser.parse_args()

    R = parse_mail()
    submit_request(R, options)
