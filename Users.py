"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Users.py,v 1.1 2004/10/10 11:03:10 ajung Exp $
"""


from Globals import InitializeClass, Persistent
from BTrees.OOBTree import OOBTree 
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import *

from config import ManageCollector

class Users(Persistent):
    
    security = ClassSecurityInfo()

    def __init__(self):
        self.clear()

    security.declareProtected(ManageCollector, 'clear')
    def clear(self):
        self._ro = OOBTree()   # role -> [users]

    security.declareProtected('View', 'getUsers')
    def getUsers(self):             
        """ return mapping role -> [users] """
        d = {}
        for role in self._ro.keys():
            d[role] = list(self._ro[role])
        return d

    security.declareProtected(ManageCollector, 'addUser')
    def addUser(self, user, role):
        """ add user with role """
        if not self._ro.has_key(role):
            self._ro[role] = []
        self._ro[role].append(user)

    security.declareProtected(ManageCollector, 'addRole')
    def addRole(self, role):
        """ initialize a new role """
        if self._ro.has_key(role):
            raise ValueError(self.Translate('role_exists', 'Role exists: $role', role=role))
        self._ro[role] = []

    security.declareProtected(ManageCollector, 'setUsersForRole')
    def setUsersForRole(self, role, users):
        """ set all users for a given role """
        self._ro[role] = list(users)

    security.declareProtected(ManageCollector, 'removeRoleFromUser')
    def removeRoleFromUser(self, user, role):
        """ remove a role from a user """
        if not self._ro.has_key(role):
            raise ValueError(self.Translate('no_such_role', 'No such role: $role', role=role))
        try:
            del self._ro[role][user]
        except KeyError:
            raise ValueError(self.Translate('no_user_with_role', 'No user $user with role $role found', user=user, role=role))

    security.declareProtected('View', 'getRolesForUser')
    def getRolesForUser(self, user):
        """ return a list of role for user """
        roles = [r for r in self._ro.keys() if user in self._ro[r]]

    security.declareProtected('View', 'getUsersForRole')
    def getUsersForRole(self, role):
        """ return all users for a given role """
        if not self._ro.has_key(role):
            return []
        return self._ro[role]


InitializeClass(Users) 

