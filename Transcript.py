"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Transcript.py,v 1.6 2003/09/11 04:12:36 ajung Exp $
"""

import time 

from Globals import Persistent, InitializeClass
from Acquisition import Implicit
from BTrees.IOBTree import IOBTree
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
        self._items = IOBTree()

    def __len__(self): 
        return len(self._items)

    security.declareProtected(CMFCorePermissions.View, 'add')
    def add(self, event):
        self._items[int(time.time())] = event

    security.declareProtected(CMFCorePermissions.View, 'addComment')
    def addComment(self, comment):
        event = TranscriptEvent('comment', comment=comment)
        self.add(event)

    security.declareProtected(CMFCorePermissions.View, 'addChange')
    def addChange(self, field, old, new):
        if str(old) != str(new):
            event = TranscriptEvent('change', field=field, old=old, new=new)
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
    def getEvents(self):
        lst = list(self._items.values())
        lst.sort(lambda x,y: -cmp(x.created, y.created))
        return lst

InitializeClass(Transcript)

