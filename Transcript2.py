"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: Transcript2.py,v 1.8 2004/11/12 15:37:52 ajung Exp $
"""

import time, random 

from Globals import InitializeClass
from BTrees.OOBTree import OOBTree, difference, OOSet
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo, getSecurityManager

from Products.CMFCore.CMFCorePermissions import *

from config import ManageCollector

allowed_states = ('public', 'private', 'system', 'other')


class BaseEvent(SimpleItem):
    
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, user=None, state='private'):
        if not state in allowed_states:
            raise ValueError('Unknown state: %s' % state)
        self._creator = getSecurityManager().getUser().getUserName()
        if user:
            self._user = user 
        else:
            self._user = self._creator
        self._state = state
        self._newTimestamp()

    def _newTimestamp(self):
        self._created = time.time() + random.random() / 1000.0

    def getState(self):
        return self._state

    def getCreated(self):
        return self._created
    getTimestamp = getCreated

    def getCreator(self):
        return self._creator
    
    def getUser(self):
        return self._user

    def getType(self):
        return self.meta_type


InitializeClass(BaseEvent) 


class CommentEvent(BaseEvent):
    
    meta_type = 'comment'

    def __init__(self, comment, mimetype='text/plain', state='private'):
        BaseEvent.__init__(self, state=state)
        if not isinstance(comment, unicode):
            raise TypeError("Parameter 'comment' must be unicode")
        self._comment = comment
        self._mimetype = mimetype

    def getComment(self):
        return self._comment

    def getMimetype(self):
        return self._mimetype

InitializeClass(CommentEvent)


class ChangeEvent(BaseEvent):

    meta_type = 'change'

    def __init__(self, field, old, new, state='private'):
        BaseEvent.__init__(self, state=state)
        self._field = field
        self._old =old
        self._new = new

    def getOld(self): return self._old
    def getNew(self): return self._new
    def getField(self): return self._field

InitializeClass(ChangeEvent)


class IncrementalChangeEvent(BaseEvent):
    
    meta_type = 'incremental'

    def __init__(self, field, old, new, state='private'):
        BaseEvent.__init__(self, state=state)
        self._field = field
        self._added = list(difference(OOSet(new), OOSet(old)))
        self._removed = list(difference(OOSet(old), OOSet(new)))
            
    def getField(self): return self._field
    def getAdded(self): return self._added
    def getRemoved(self): return self._removed

InitializeClass(IncrementalChangeEvent)


class UploadEvent(BaseEvent):

    meta_type = 'upload'

    def __init__(self, fileid, comment, state='private'):
        BaseEvent.__init__(self, state=state)
        if not isinstance(comment, unicode):
            raise TypeError("Parameter 'comment' must be unicode")
        self._fileid = fileid
        self._comment = comment
            
    def getFileId(self): return self._fileid
    def getComment(self): return self._comment

InitializeClass(UploadEvent)


class ReferenceEvent(BaseEvent):

    meta_type = 'reference'

    def __init__(self, issue_id, issue_url, tracker_id, comment, state='private'):
        BaseEvent.__init__(self, state=state)
        if not isinstance(comment, unicode):
            raise TypeError("Parameter 'comment' must be unicode")
        self._issue_id = issue_id
        self._issue_url = issue_url
        self._tracker_id = tracker_id
        self._comment = comment

    def getTrackerId(self): return self._tracker_id
    def getIssueId(self): return self._issue_id
    def getIssueURL(self): return self._issue_url
    def getComment(self): return self._comment

InitializeClass(ReferenceEvent)


class ActionEvent(BaseEvent):

    meta_type = 'action'

    def __init__(self, action, state='private'):
        BaseEvent.__init__(self, state=state)
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
        while self._items.has_key(event.getCreated()):
            event._newTimestamp()
        self._items[event.getCreated()] = event

    security.declareProtected(View, 'getEvents')
    def getEvents(self, reverse=True, types=(), show_only=()):
        """ return all events sorted by timestamp in reverse order. 'show_only' is 
            a sequence of allowed states to be returned 
         """
        lst = list(self._items.values())
        if show_only:
            lst = [e for e in lst  if e.getState() in show_only]
        if types:
            lst = [e for e in lst  if e.getType() in types]
        lst.sort(lambda x,y:  cmp(x.getCreated(), y.getCreated()))
        if reverse: lst.reverse()
        return lst
    
    security.declareProtected(View, 'getEventsGrouped')
    def getEventsGrouped(self, reverse=True, types=(), show_only=()):
        """ return all events grouped by their timestamp """

        last_ts = 0; last_user = None
        result = []
        for event in self.getEvents(False, types, show_only):
            if event.getUser() != last_user or event.getCreated() - last_ts > 60  or event.getType() in ('comment', ):
                # new event
                result.append([])
            result[-1].insert(0, event)
            last_ts = event.getCreated()
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

