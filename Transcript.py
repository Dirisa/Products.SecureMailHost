"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Transcript.py,v 1.24 2004/05/14 11:10:18 ajung Exp $
"""

import time 
from types import UnicodeType, StringType

from Globals import Persistent, InitializeClass
from Acquisition import Implicit
from BTrees.OOBTree import OOBTree, OOSet, difference
from AccessControl import ClassSecurityInfo 
from Products.CMFCore.CMFCorePermissions import *

import util
from config import ManageCollector, EditCollectorIssue

class TranscriptEvent(Persistent, Implicit):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, type, **kw):
        self.__dict__.update(kw)
        self.type = type
        created = kw.get('created', None)
        if created is not None: self.created = created
        else: self.created = time.time()

        user = kw.get('user', None)
        if user: self.user = user
        else: self.user = util.getUserName()

    def __str__(self):
        return 'TranscriptEvent(%s)' % ','.join(['%s=%s' % (k,v) for k,v in self.__dict__.items()])
    __repr__ = __str__

    security.declarePublic('getTimestamp')
    def getTimestamp(self):             
        return self.created

    security.declarePublic('getType')
    def getType(self):
        return self.type

    security.declarePublic('getValue')
    def getValue(self, k):
        return getattr(self, k)

    security.declarePublic('getUser')
    def getUser(self):
        return self.user


InitializeClass(TranscriptEvent) 


class Transcript(Persistent, Implicit):
    """ container class for all TranscriptEntry objects """

    security = ClassSecurityInfo()

    def __init__(self):
        self._items = OOBTree()
        self.encoding = 'iso-8859-15' 

    def __len__(self): 
        return len(self._items)

    security.declareProtected(View, 'add')
    def add(self, event):
        created = event.created
        while self._items.has_key(created):
            created += 0.01

        self._items[created] = event

    replace = add  # make an alias to provide support to replace an event

    security.declarePublic('setEncoding')
    def setEncoding(self, encoding):             
        self.encoding = encoding

    def conv(self, item):
        if isinstance(item, StringType):
            return unicode(item, self.encoding)
        return item

    security.declareProtected(View, 'addComment')
    def addComment(self, comment, text_format='plain', user=None, created=None):
        if not isinstance(comment, UnicodeType):
            raise TypeError('comment must be unicode')
        event = TranscriptEvent('comment', comment=comment, 
                                 text_format=text_format, 
                                 user=user, created=created)
        self.add(event)

    security.declareProtected(View, 'addChange')
    def addChange(self, field, old, new, user=None, created=None):
        if repr(old) != repr(new):
            event = TranscriptEvent('change', field=field, 
                                     old=self.conv(old), 
                                     new=self.conv(new), 
                                     user=user, created=created)
            self.add(event)

    security.declareProtected(View, 'addIncrementalChange')
    def addIncrementalChange(self, field, old, new, user=None, created=None):

        added = list(difference(OOSet(new), OOSet(old)))
        removed = list(difference(OOSet(old), OOSet(new)))

        if removed or added:
            event = TranscriptEvent('incrementalchange', field=field, 
                                     added=self.conv(added), 
                                     removed=self.conv(removed), 
                                     user=user, created=created)
            self.add(event)

    security.declareProtected(View, 'addReference')
    def addReference(self, tracker, ticketnum, comment, user=None, created=None):
        event = TranscriptEvent('reference', tracker=tracker, 
                                 ticketnum=ticketnum, 
                                 comment=self.conv(comment), 
                                 user=user, 
                                 created=created)
        self.add(event)

    security.declareProtected(View, 'addUpload')
    def addUpload(self, fileid, comment, user=None, created=None):
        event = TranscriptEvent('upload', fileid=fileid, 
                                 comment=self.conv(comment), 
                                 user=user, created=created)
        self.add(event)

    security.declareProtected(View, 'addAction')
    def addAction(self, action, user=None):
        event = TranscriptEvent('action', action=action, user=user)
        self.add(event)

    security.declareProtected(View, 'getEvents')
    def getEvents(self, reverse=1):
        """ return all events sorted by timestamp in reverse order """
        lst = list(self._items.values())
        lst.sort(lambda x,y:  cmp(x.created, y.created))
        if reverse: lst.reverse()
        return lst
    
    security.declareProtected(View, 'getEventsGrouped')
    def getEventsGrouped(self, reverse=1):
        """ return all events grouped by their timestamp """

        last_ts = 0; last_user = None
        result = []
        for event in self.getEvents(reverse=0):
            if event.getUser() != last_user or event.getTimestamp() - last_ts > 60  or event.getType() in ('comment', ):
                # new event
                result.append([])
            result[-1].insert(0, event)
            last_ts = event.getTimestamp()
            last_user = event.getUser()

        if reverse: result.reverse()
        return result

    security.declareProtected(EditCollectorIssue, 'modifyEntry')
    def modifyEntry(self, timestamp, **kw):
        """ modify an entry given by its timestamp """
        for event in self.getEvents():
            if str(event.getTimestamp()) == str(timestamp):
                for k,v in kw.items():
                    setattr(event, k, v)
                print 'modifiziert'                

    security.declareProtected(ManageCollector, 'migrateUnicode')
    def migrateUnicode(self):
        """ migrate all events to unicode """
        for ev in self.getEvents():
            for k,v in ev.__dict__.items():
                if k in ('created', 'user', 'type'): continue
                if isinstance(v, StringType):
                    setattr(ev, k, self.conv(v))
    
    
InitializeClass(Transcript)

