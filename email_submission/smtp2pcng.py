#!/usr/local/bin/python2.3

"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: smtp2pcng.py,v 1.14 2004/04/14 17:10:25 ajung Exp $
"""

""" Gateway to submit issues through email to a PloneCollectorNG instance """

import sys, os, logging, base64, logging, time
import httplib, urllib, urlparse
from ConfigParser import ConfigParser
from cStringIO import StringIO
from optparse import OptionParser
import email
from email.Header import decode_header 

CFG_FILE = '.smtp2pcng.cfg'
MAX_LENGTH = 32768

# Spool directories
SPOOL_PENDING = os.path.join(os.getcwd(), 'pcng_spool', 'unprocessed')
SPOOL_ERROR = os.path.join(os.getcwd(), 'pcng_spool', 'error')
SPOOL_DONE = os.path.join(os.getcwd(), 'pcng_spool', 'processed')

for d in (SPOOL_PENDING, SPOOL_DONE, SPOOL_ERROR):
    if not os.path.exists(d):
        os.makedirs(d)

# Configuration
config = ConfigParser()
config.read([CFG_FILE, os.path.expanduser('~/%s' % CFG_FILE)])

# Logger stuff
LOG = logging.getLogger('myapp')
hdlr = logging.FileHandler('smtp2pcng.log')
hdlr1 = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(process)s %(message)s')
hdlr.setFormatter(formatter)
hdlr1.setFormatter(formatter)
LOG.addHandler(hdlr)
LOG.addHandler(hdlr1)
LOG.setLevel(logging.DEBUG)

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

        section = options.configuration
        if not config.has_section(section):
            raise ValueError("Section '%s' not found in configuration file" % section)
        for op in ('url', 'username', 'password'):
            if not config.has_option(section, op):
                raise ValueError("Section '%s' has no option '%s'" % (section, op))

        options.url = config.get(section, 'url')
        options.username = config.get(section, 'username')
        options.password = config.get(section, 'password')
        if config.has_section('default'):
            if config.has_option('default', 'maxlength'):
                options.max_length = int(config.get('default', 'maxlength'))     
            else:
                options.max_length = MAX_LENGTH


    if options.filename is not None:
        LOG.debug('Reading from: %s' % options.filename)
        text = open(options.filename).read()
    else:
        print >>sys.stderr, 'Reading mail from stdin'
        text = sys.stdin.read()

    LOG.debug('Length of message: %d bytes' % len(text))
    if len(text) > options.max_length:
        raise RuntimeError('Message size exceeds allowed length of %d bytes' % options.max_length)

    msg = email.message_from_string(text)
    R = Result()
    R.original_message = text

    for part in msg.walk():
        ct = part.get_content_type() 
        encoding = part.get_charset() or 'iso-8859-15'

        if part.has_key("From"):
            R.sendername, R.senderaddress = email.Utils.parseaddr(part.get("From"))
            R.reply_to = R.senderaddress
            LOG.debug('From=%s,%s' % (R.sendername, R.senderaddress))

        if part.has_key("Reply-To"):
            R.reply_to = email.Utils.parseaddr(part.get("Reply-To"))[1]
            LOG.debug('Reply-To=%s' % (R.reply_to))

        if part.has_key("Subject"):
            R.subject = decode_header(part.get("Subject"))[0][0]
            LOG.debug('Subject=%s' % (R.subject))

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


def handle_response(R, status, reason, data):

    LOG.debug('Status: %s' % status)
    LOG.debug('Reason: %s' % reason)
    LOG.debug('Data: %s' % data)

    if status == 200:    # OK 
        LOG.info('Submission ok')
        fname = os.path.join(SPOOL_DONE, str(time.time()))
        open(fname, 'w').write(R.original_message)

    elif status == 401:  # Unauthorized
        LOG.info('Submission unauthorized')
        fname = os.path.join(SPOOL_ERROR, str(time.time()))
        open(fname, 'w').write(R.original_message)

    elif status == 404:  # NotFound
        LOG.info('Submission URL not found')
        fname = os.path.join(SPOOL_ERROR, str(time.time()))
        open(fname, 'w').write(R.original_message)


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
    parser.add_option('-C', '--configuration', dest='configuration', 
                      help='Section from configuration file to be used', default=None)
    options, args = parser.parse_args()

    LOG.info('-'*75)
    LOG.debug(options)

    try:
        R = parse_mail(options)
        status, reason, data = submit_request(R, options)
        handle_response(R, status, reason, data)
    except:
        LOG.error('Error processing mail', exc_info=sys.exc_info())        

    LOG.info('End')
