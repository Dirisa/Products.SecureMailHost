"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Result.py,v 1.2 2004/09/11 12:19:05 ajung Exp $
"""

from cStringIO import StringIO

class Result:
    """ A simple result class """

    def __init__(self):
        self.attachments = []
        self.key = ''
        self.collector_abr = ''
        self.issue_id = ''

    def addAttachment(self, data, mimetype, filename):
        self.attachments.append( (data, mimetype, filename))

    def getAttachments(self):
        return self.attachments

    def toXML(self):
        IO = StringIO()
        IO.write('<?xml version="1.0" encoding="utf-8"?>\n')
        IO.write('<issue>\n')
        for a in ('sendername', 'senderaddress', 'reply_to', 'body', 'key', 'issue_id', 'collector_abr'):
            IO.write('<%s>%s</%s>\n' % (a, getattr(self, a), a))
        
        # We need to escape the subject a bit to avoid trouble
        s = self.subject.replace('&', '&amp;')
        IO.write('<subject>%s</subject>\n' % s)

        for a in self.getAttachments():
            IO.write('<attachment mimetype="%s" filename="%s">\n' % a[1:])
            IO.write(base64.encodestring(a[0]))
            IO.write('</attachment>\n')
            
        IO.write('</issue>\n')
        return IO.getvalue()
