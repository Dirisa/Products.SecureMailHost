#!/usr/local/bin/python2.3

"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: smtp2pcng.py,v 1.18 2004/09/11 12:19:05 ajung Exp $
"""

""" Gateway to submit issues through email to a PloneCollectorNG instance """

import sys, os, base64, logging, time, re
import httplib, urllib, urlparse
from ConfigParser import ConfigParser
from cStringIO import StringIO
from optparse import OptionParser
import email
from email.Header import decode_header 

from Result import Result
from util import getLogger, getConfiguration, update_options

# Spool directories
SPOOL_PENDING = os.path.join(os.getcwd(), 'pcng_spool', 'unprocessed')
SPOOL_ERROR = os.path.join(os.getcwd(), 'pcng_spool', 'error')
SPOOL_DONE = os.path.join(os.getcwd(), 'pcng_spool', 'processed')

for d in (SPOOL_PENDING, SPOOL_DONE, SPOOL_ERROR):
    if not os.path.exists(d):
        os.makedirs(d)

LOG = getLogger()
CONFIG = getConfiguration()

def parse_mail(options):
    """ retrieve email from stdin or a file and return a parsed
        Result instance.
    """
 
    if options.filename is not None:
        LOG.debug('Reading from: %s' % options.filename)
        text = open(options.filename).read()
    else:
        print >>sys.stderr, 'Reading mail from stdin'
        text = sys.stdin.read()

    LOG.debug('Length of message: %d bytes' % len(text))
    if len(text) > options.max_length:
        raise RuntimeError('Message size exceeds allowed length of %d bytes' % options.max_length)

    return process_email_from_text(text)


def process_email_from_text(text):
    """ process an email represented as plain text """

    # convert to Python internal message format
    msg = email.message_from_string(text)

    R = Result()
    R.original_message = text

    for part in msg.walk():
        ct = part.get_content_type() 
        encoding = part.get_charset() or 'iso-8859-15'

        cd = part['content-disposition'] or ''
        if cd.find('pcng.key') > -1:
            R.key = part.get_payload()
            continue

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
            mo = re.search('\[(.*?)/(.*?)\]', R.subject)
            if mo:
                R.collector_abr = mo.group(1)
                R.issue_id = mo.group(2)

        if ct in ('text/plain',):
            payload = part.get_payload(decode=1)
            if payload:
                R.body = unicode(payload, encoding).encode('utf-8')
            else:
                R.body = ''
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

    if options.configuration:
        update_options(options, CONFIG)

    try:
        R = parse_mail(options)
        status, reason, data = submit_request(R, options)
        handle_response(R, status, reason, data)
    except:
        LOG.error('Error processing mail', exc_info=sys.exc_info())        

    LOG.info('End')
