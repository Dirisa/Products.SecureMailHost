"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com

Published under the MIT Public License

$Id: Transcript.py,v 1.2 2003/09/06 06:36:00 ajung Exp $
"""

from types import StringType, ListType, TupleType
import os

from Globals import Persistent, InitializeClass
from AccessControl import ClassSecurityInfo, getSecurityManager
from DateTime.DateTime import DateTime

class Transcript(Persistent):
    """ container class for all TranscriptEntry objects """

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self):
        self._items = []

    security.declarePublic('add')
    def add(self, entry):

        assert isinstance(entry, TranscriptEntry)
        if len(entry) > 0:
            entry.setNumber(len(self) + 1)
            self._items.insert(0, entry)

    security.declarePublic('addTranscriptChangeEvent')
    def addTranscriptChangeEvent(self, field, old, new):
        entry = TranscriptEntry('system')
        entry.addChange(field, old, new)
        self.add(entry)


    def addComment(self, comment):
        te = TranscriptEntry(getSecurityManager().getUser().getUserName())  
        te.addComment(comment)
        self.add(te)

    def addChange(self, field, old, new):
        te = TranscriptEntry(getSecurityManager().getUser().getUserName())  
        te.addChange(field, old, new)
        self.add(te)

    def __len__(self): return len(self._items)

    def __getitem__(self, n): 
        return self._items[n]


##################################################################
# Transcript changes
##################################################################

## TODO: All Event classes should subclass a common base class
## that provides at least a getType() method

class CommentEvent(Persistent):
    """ transcript comments """

    meta_type = "CommentEvent"

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, comment):
        self._comment = comment

    security.declarePublic('getComment')
    def getComment(self):
        return self._comment

    def __str__(self):
        return self._comment

    def asXML(self):
        return '<comment>%s</comment>' % self._comment

InitializeClass(CommentEvent)


class ReferenceEvent(Persistent):
    """ transcript references """

    meta_type = "ReferenceEvent"

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, tracker, ticketnumber, comment):
        self._tracker = tracker
        self._ticketnumber = ticketnumber
        self._comment = comment

    security.declarePublic('getTracker')
    def getTracker(self):
        return self._tracker

    security.declarePublic('getTicketNumber')
    def getTicketNumber(self):
        return self._ticketnumber

    security.declarePublic('getComment')
    def getComment(self):
        return self._comment

    def __str__(self):
        return '%s #%s (%s)' % \
             (self._tracker, self._ticketnumber, self._comment)

    def asXML(self):
        return '<reference><tracker>%s<tracker><ticketnumber>%s</ticketnumber><comment>%s</comment></reference>' % \
             (self._tracker, self._ticketnumber, self._comment)

InitializeClass(ReferenceEvent)


class UploadEvent(Persistent):
    """ transcript references """

    meta_type = "UploadEvent"

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, fileid, comment):
        self._fileid = fileid
        self._comment = comment

    security.declarePublic('getFileId')
    def getFileId(self):
        return os.path.split(self._fileid.replace('\\','/'))[1]

    security.declarePublic('getComment')
    def getComment(self):
        return self._comment

    def __str__(self):
        return '%s (%s)' % (self._fileid, self._comment)

    def asXML(self):
        return '<upload><file>%s</file><comment>%s</comment></upload>' % (self._fileid, self._comment)

InitializeClass(UploadEvent)
        
     

class ChangeEvent(Persistent):
    """ simple event class for changes of StringType properties """

    meta_type = 'ChangeEvent'

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, field, old , new):
        self._field = field
        self._old = old
        self._new = new

    security.declarePublic('getField')
    def getField(self): 
        return self._field

    security.declarePublic('getOld')
    def getOld(self):
        return self._old

    security.declarePublic('getNew')
    def getNew(self):
        return self._new

    security.declarePublic('getType')
    def getType(self):
        return self.meta_type

    def __str__(self):
        return "%s: '%s' ->  '%s'" % \
            (self._field, self._old, self._new)

    def asXML(self):
        return "<change field=\"%s\"><old>%s</old><new>%s</new></change>'" % \
            (self._field, self._old, self._new)

InitializeClass(ChangeEvent)


class IncrementalChangeEvent(ChangeEvent):
    """ simple event class for changes of ListType properties """

    meta_type = 'IncrementalChangeEvent'

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, field, old, new):
        self._field = field
        self._added = []
        self._removed = []

        for item in old:
            if not item in new:
                self._removed.append(item)

        for item in new:
            if not item in old:
                self._added.append(item)

    security.declarePublic('getAdded')
    def getAdded(self):
        return self._added

    security.declarePublic('getAddedAsString')
    def getAddedAsString(self):
        return ', '.join(self._added)

    security.declarePublic('getRemoved')
    def getRemoved(self):
        return self._removed

    security.declarePublic('getRemovedAsString')
    def getRemovedAsString(self):
        return ', '.join(self._removed)

    def __nonzero__(self):
        return len(self._added) > 0 or len(self._removed) > 0

    def __str__(self):
        return '%s: added: %s, removed: %s' % \
            (self._field, self._added, self._removed)

    def asXML(self):
        return "<incrementalchange field=\"%s\"><removed>%s</removed><added>%s</added></incrementalchange>'" % \
            (self._field, ','.join(self._removed), ','.join(self._added))

InitializeClass(IncrementalChangeEvent)


class TranscriptEntry(Persistent):
    """ container class for multiple changes and comments """

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, user=None):
        if user is None:
            user = getSecurityManager().getUser().getUserName()

        self._timestamp = DateTime()
        self._changes = []
        self._user = user
        self._comments = []
        self._number = None
        self._references = []
        self._uploads = []

    def addChange(self, field, old, new):
        
        if isinstance(old, ListType) or isinstance(old, TupleType):
            event = IncrementalChangeEvent(field, old, new)
            if event:
                self._changes.append(event)
        else:
            self._changes.append(ChangeEvent(field, old, new))

    def addComment(self, comment):
        self._comments.append(CommentEvent(comment))

    def addReference(self, tracker, ticketnumber, comment):
        self._references.append(ReferenceEvent(tracker, ticketnumber, comment))

    def addUpload(self, fileid, comment=''):
        self._uploads.append(UploadEvent(fileid, comment))

    def setNumber(self, number):
        self._number = number

    security.declarePublic('getNumber')
    def getNumber(self):   
        return self._number

    security.declarePublic('getChanges')
    def getChanges(self):   
        return self._changes

    security.declarePublic('getComments')
    def getComments(self):
        return self._comments

    security.declarePublic('getUploads')
    def getUploads(self):
        return self._uploads

    security.declarePublic('getReferences')
    def getReferences(self):
        return self._references

    security.declarePublic('getUser')
    def getUser(self):      
        return self._user

    security.declarePublic('getTimestamp')
    def getTimestamp(self): 
        return self._timestamp

    def __len__(self):
        return len(self._changes) + len(self._comments) + len(self._uploads) + len(self._references)

    def __str__(self):
        return '%s %s: (%s)' % \
            (self._timestamp.strftime('%d.%m.%Y %H:%M:%S'), \
             self._user, \
             ', '.join( [ str(change) for change in self._changes ] ))

    def asXML(self):
        s = '<entry timestamp="%s" user="%s" number="%s">\n' % \
            (self._timestamp.ISO(), self._user, self._number)
        for event in self._changes + self._comments + self._uploads + self._references:
            s +=  "    " + event.asXML() + "\n"
        s += '</entry>'
        return s

InitializeClass(TranscriptEntry)    

