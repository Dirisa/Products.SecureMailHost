from Globals import InitializeClass
from Globals import Persistent
from AccessControl import ClassSecurityInfo, getSecurityManager
from types import StringType, ListType, TupleType


class ReferencesManager(Persistent):
    """ container class for all references """

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self):
        self._references = []

    security.declarePublic('add')
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
    security.declareObjectPublic()

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
        return '%s: %s' % (self._url, self._comment)

    __repr__ = __str__

InitializeClass(Reference)
