"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Transcript2.py,v 1.2 2004/07/22 19:55:05 ajung Exp $
"""

import time, random 

from Globals import Persistent, InitializeClass
from Acquisition import Implicit
from BTrees.OOBTree import OOBTree, difference, OOSet
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo, getSecurityManager

from Products.CMFCore.CMFCorePermissions import *

from config import ManageCollector, EditCollectorIssue

#class BaseEvent(Persistent, Implicit):
class BaseEvent(SimpleItem):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, user=None, public=True):
        self._creator = getSecurityManager().getUser().getUserName()
        self._user = user 
        self._public = public
        self.newTimestamp()

    def newTimestamp(self):
        self._created = time.time() + random.random() / 1000.0

    def isPublic(self):
        return self._public

    def created(self):
        return self._created
    getTimestamp = created

    def setCreated(self, created):
        self._created = created

    def Creator(self):
        return self._creator
    
    def getUser(self):
        return self._user

    def getType(self):
        return self.meta_type


InitializeClass(BaseEvent) 


class CommentEvent(BaseEvent):
    
    meta_type = 'comment'

    def __init__(self, comment, mimetype='text/plain', public=True):
        BaseEvent.__init__(self, public=public)
        if not isinstance(comment, unicode):
            raise TypeError("Parameter 'comment' must be unicode")
        self._comment = comment
        self._mimetype = mimetype

    def getComment(self):
        return self._comment

InitializeClass(CommentEvent)


class ChangeEvent(BaseEvent):

    meta_type = 'change'

    def __init__(self, field, old, new, public=True):
        BaseEvent.__init__(self, public=public)
        self._field = field
        self._old =old
        self._new = new

    def getField(self): return self._field
    def getOld(self): return self._old
    def getNew(self): return self._new

InitializeClass(ChangeEvent)


class IncrementalChangeEvent(BaseEvent):
    
    meta_type = 'incremental'

    def __init__(self, field, old, new, public=True):
        BaseEvent.__init__(self, public=public)
        self._field = field
        self._added = list(difference(OOSet(new), OOSet(old)))
        self._removed = list(difference(OOSet(old), OOSet(new)))
            
    def getField(self): return self._field
    def getAdded(self): return self._added
    def getRemoved(self): return self._removed

InitializeClass(IncrementalChangeEvent)


class UploadEvent(BaseEvent):

    meta_type = 'upload'

    def __init__(self, fileid, comment, public=True):
        BaseEvent.__init__(self, public=public)
        if not isinstance(comment, unicode):
            raise TypeError("Parameter 'comment' must be unicode")
        self._fileid = fileid
        self._comment = comment
            
    def getFileId(self): return self._fileid
    def getComment(self): return self._comment

InitializeClass(UploadEvent)


class ReferenceEvent(BaseEvent):

    meta_type = 'reference'

    def __init__(self, tracker, ticketnum, comment, public=True):
        BaseEvent.__init__(self, public=public)
        if not isinstance(comment, unicode):
            raise TypeError("Parameter 'comment' must be unicode")
        self._tracker = tracker
        self._ticketnum = ticketnum
        self._comment = comment

    def getTracker(self): return self._tracker
    def getTicketNum(self): return self._ticketnum
    def getComment(self): return self._comment

InitializeClass(ReferenceEvent)


class ActionEvent(BaseEvent):

    meta_type = 'action'

    def __init__(self, action, public=True):
        BaseEvent.__init__(self, public=public)
        self._action = action

    def getAction(self): return self._action

InitializeClass(ActionEvent)




class Transcript2(SimpleItem):
    """ container class for all event objects """

    security = ClassSecurityInfo()

    def __init__(self):
        self._items = OOBTree()

    def __len__(self): 
        return len(self._items)

    security.declareProtected(View, 'add')
    def add(self, event):
        while self._items.has_key(event.created()):
            event.newTimestamp()

        self._items[event.created()] = event

    security.declareProtected(View, 'getEvents')
    def getEvents(self, reverse=1, filter_nonpublic=True):
        """ return all events sorted by timestamp in reverse order """
        lst = list(self._items.values())
        if filter_nonpublic:
            lst = [e for e in lst  if e.isPublic()]
        lst.sort(lambda x,y:  cmp(x.created(), y.created()))
        if reverse: lst.reverse()
        return lst
    
    security.declareProtected(View, 'getEventsGrouped')
    def getEventsGrouped(self, reverse=1, filter_nonpublic=True):
        """ return all events grouped by their timestamp """

        last_ts = 0; last_user = None
        result = []
        for event in self.getEvents(reverse=0, filter_nonpublic=filter_nonpublic):
            if event.getUser() != last_user or event.created() - last_ts > 60  or event.getType() in ('comment', ):
                # new event
                result.append([])
            result[-1].insert(0, event)
            last_ts = event.created()
            last_user = event.getUser()

        if reverse: result.reverse()
        return result

    security.declareProtected(ManageCollector, 'deleteEvent')
    def deleteEvent(self, timestamp):
        """ Delete an entry given by its timestamp """
        
        for k,v in self._items.items():
            if str(k) == str(timestamp):
                del self._items[k]
                break
    
    security.declareProtected(ManageCollector, 'modifyEvent')
    def modifyEvent(self, timestamp, comment):
        """ Update a CommentEvent """
        
        for k,v in self._items.items():
            if str(k) == str(timestamp):
                self._items[k]._comment = comment

InitializeClass(Transcript2)

