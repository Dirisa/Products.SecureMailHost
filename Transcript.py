"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Transcript.py,v 1.16 2003/11/04 13:44:55 ajung Exp $
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

        for k,v in kw.items():
            setattr(self, k, v)
        
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

    def __len__(self): 
        return len(self._items)

    security.declareProtected(CMFCorePermissions.View, 'add')
    def add(self, event):
        created = event.created
        while self._items.has_key(created):
            created += 0.01

        self._items[created] = event

    replace = add  # make an alias to provide support to replace an event

    security.declareProtected(CMFCorePermissions.View, 'addComment')
    def addComment(self, comment, user=None, created=None):
        event = TranscriptEvent('comment', comment=comment, user=user, created=created)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addChange')
    def addChange(self, field, old, new, user=None, created=None):
        if str(old) != str(new):
            event = TranscriptEvent('change', field=field, old=old, new=new, user=user, created=created)
            self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addIncrementalChange')
    def addIncrementalChange(self, field, old, new, user=None, created=None):

#        assert isinstance(old, (list, tuple)) and isinstance(new, (list, tuple))
        added = list(difference(OOSet(new), OOSet(old)))
        removed = list(difference(OOSet(old), OOSet(new)))

        if removed or added:
            event = TranscriptEvent('incrementalchange', field=field, added=added, removed=removed, user=user, created=created)
            self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addReference')
    def addReference(self, tracker, ticketnum, comment, user=None, created=None):
        event = TranscriptEvent('reference', tracker=tracker, ticketnum=ticketnum, comment=comment, user=user, created=created)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addUpload')
    def addUpload(self, fileid, comment, user=None, created=None):
        event = TranscriptEvent('upload', fileid=fileid, comment=comment, user=user, created=created)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addAction')
    def addAction(self, action, user=None):
        event = TranscriptEvent('action', action=action, user=user)
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
    
InitializeClass(Transcript)

