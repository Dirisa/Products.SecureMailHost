#!/usr/local/bin/python2.3

"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: smtp2pcng.py,v 1.9 2004/04/12 16:20:01 ajung Exp $
"""

""" Gateway to submit issues through email to a PloneCollectorNG instance """

import sys, os, logging, base64
import httplib, urllib, urlparse
from ConfigParser import ConfigParser
from cStringIO import StringIO
from optparse import OptionParser
import email
from email.Header import decode_header 

CFG_FILE = '.smtp2pcng.cfg'

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
        for a in ('sendername', 'senderaddress', 'reply_to', 'subject', 'body'):
            IO.write('<%s>%s</%s>\n' % (a, getattr(self, a), a))

        for a in self.getAttachments():
            IO.write('<attachment mimetype="%s" filename="%s">\n' % a[1:])
            IO.write(base64.encodestring(a[0]))
            IO.write('</attachment>\n')
            
        IO.write('</issue>\n')
        return IO.getvalue()
    

def parse_mail(options):

    # parse configuration
    if options.configuration:
        config = ConfigParser()
        config.read([CFG_FILE, os.path.expanduser('~/%s' % CFG_FILE), options.configuration_file])
        section = options.configuration
        if not config.has_section(section):
            raise ValueError("Section '%s' not found in configuration file" % section)
        for op in ('url', 'username', 'password'):
            if not config.has_option(section, op):
                raise ValueError("Section '%s' has no option '%s'" % (section, op))

        options.url = config.get(section, 'url')
        options.username = config.get(section, 'username')
        options.password = config.get(section, 'password')

    if options.filename is not None:
        text = open(options.filename).read()
    else:
        print >>sys.stderr, 'Reading mail from stdin'
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
              }
    if options.username and options.password:
        headers['Authorization'] = 'Basic ' + base64.encodestring('%s:%s' % (options.username, options.password))[:-1]

    f = urlparse.urlparse(options.url)
    conn = httplib.HTTPConnection(f[1])
    conn.request("POST", f[2], params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return (response.status, response.reason, data)


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-f', '--file', dest='filename', 
                      help='File to read from email from', default=None)
    parser.add_option('-U', '--url', dest='url', 
                      help='PloneCollectorNG URL to add issues', default=None)
    parser.add_option('-u', '--username', dest='username', 
                      help='Plone user name', default='')
    parser.add_option('-p', '--password', dest='password', 
                      help='Plone user password', default='')
    parser.add_option('-c', '--configuration-file', dest='configuration_file', 
                      help='Path to configuration file (~/%s)' % CFG_FILE, default='~/%s' % CFG_FILE)
    parser.add_option('-C', '--configuration', dest='configuration', 
                      help='Section from configuration file to be used', default=None)

    options, args = parser.parse_args()
    R = parse_mail(options)
    print submit_request(R, options)
