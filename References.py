"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: References.py,v 1.5 2003/09/11 04:12:51 ajung Exp $
"""

from Globals import InitializeClass
from Globals import Persistent
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore import CMFCorePermissions
from types import StringType, ListType, TupleType


class ReferencesManager(Persistent):
    """ container class for all references """

    security = ClassSecurityInfo()

    def __init__(self):
        self._references = []

    security.declareProtected(CMFCorePermissions.View, 'add')
    def add(self, ref):
        self._references.insert(0, ref)
        self._p_changed = 1
            
    def __len__(self): return len(self._references)

    def __getitem__(self, n): 
        return self._references[n]

    def __str__(self):
        return str(self._references)

InitializeClass(ReferencesManager)


class Reference(Persistent):

    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

    def __init__(self, tracker, ticketnumber, comment):
        self._tracker = tracker
        self._ticketnumber = ticketnumber
        self._comment = comment

        if not (tracker and ticketnumber):
            raise ValueError, 'References requires URL *and* Comment as parameters'
                            
    security.declarePublic('getTracker')
    def getTracker(self):
        return self._tracker

    security.declarePublic('getTicketNumber')
    def getTicketNumber(self):
        return self._ticketnumber

    security.declarePublic('getURL')
    def getURL(self):
        return self._tracker + '/' + self._ticketnumber 

    security.declarePublic('getComment')
    def getComment(self):
        return self._comment

    def __str__(self):
        return '%s (#%s): %s' % (self._tracker, self._ticketnumber, self._comment)

    __repr__ = __str__

InitializeClass(Reference)
