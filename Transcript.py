"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Transcript.py,v 1.10 2003/09/19 09:54:59 ajung Exp $
"""

import time 

from Globals import Persistent, InitializeClass
from Acquisition import Implicit
from BTrees.OOBTree import OOBTree, OOSet, difference
from AccessControl import ClassSecurityInfo 
from Products.CMFCore import CMFCorePermissions

import util

class TranscriptEvent(Persistent, Implicit):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, type, **kw):
        self.type = type
        self.created = time.time()
        self.user = util.getUserName()
        for k,v in kw.items():
            setattr(self, k, v)

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

    def __len__(self): 
        return len(self._items)

    security.declareProtected(CMFCorePermissions.View, 'add')
    def add(self, event):
        self._items[time.time()] = event

    security.declareProtected(CMFCorePermissions.View, 'addComment')
    def addComment(self, comment):
        event = TranscriptEvent('comment', comment=comment)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addChange')
    def addChange(self, field, old, new):
        if str(old) != str(new):
            event = TranscriptEvent('change', field=field, old=old, new=new)
            self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addIncrementalChange')
    def addIncrementalChange(self, field, old, new):

        assert isinstance(old, (list, tuple)) and isinstance(new, (list, tuple))
        added = list(difference(OOSet(new), OOSet(old)))
        removed = list(difference(OOSet(old), OOSet(new)))

        if removed or added:
            event = TranscriptEvent('incrementalchange', field=field, added=added, removed=removed)
            self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addReference')
    def addReference(self, tracker, ticketnum, comment):
        event = TranscriptEvent('reference', tracker=tracker, ticketnum=ticketnum, comment=comment)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addUpload')
    def addUpload(self, fileid, comment):
        event = TranscriptEvent('upload', fileid=fileid, comment=comment)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'getEvents')
    def getEvents(self, reverse=1):
        """ return all events sorted by timestamp in reverse order """
        lst = list(self._items.values())
        lst.sort(lambda x,y:  cmp(x.created, y.created))
        if reverse: lst.reverse()
        return lst
    
    security.declareProtected(CMFCorePermissions.View, 'getEventsGrouped')
    def getEventsGrouped(self, reverse=1):
        """ return all events grouped by their timestamp """

        last_ts = 0; last_user = None
        result = list()
        for event in self.getEvents(reverse=0):
            if event.getUser() != last_user or event.getTimestamp() - last_ts > 60  or event.getType() == 'comment':
                # new event
                result.append([])
            result[-1].append(event)
            last_ts = event.getTimestamp()
            last_user = event.getUser()

        if reverse: result.reverse()
        return result
    
InitializeClass(Transcript)

