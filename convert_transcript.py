"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: convert_transcript.py,v 1.2 2004/07/22 19:55:05 ajung Exp $
"""

from Transcript2 import *

def convert2(T1, T2):
    """ convert from Transcript to Transcript2 """

    for e in T1.getEvents():
       
        if e.getType() == 'comment':
            e2 = CommentEvent(e.getValue('comment'))

        elif e.getType() == 'change':
            e2 = ChangeEvent(e.field, e.old, e.new)

        elif e.getType() == 'incrementalchange':
            e2 = IncrementalChangeEvent(e.field, [], [])
            e2._added = e.added
            e2._removed = e.removed

        elif e.getType() == 'upload':
            e2 = UploadEvent(e.fileid, e.comment)

        elif e.getType() == 'reference':
            e2 = ReferenceEvent(e.tracker, e.ticketnum, e.comment)

        elif e.getType() == 'action':
            e2 = ActionEvent(e.action)

        else:
            raise TypeError('unknown event: %s' % e.getType())

        e2.setCreated(e.getTimestamp())
        e2._user = e2._creator = e.user
        T2.add(e2)
