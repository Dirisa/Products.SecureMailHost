"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: WatchList.py,v 1.4 2003/10/12 09:38:52 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import  ClassSecurityInfo, Unauthorized
from Products.CMFCore import CMFCorePermissions
from ZODB.PersistentList import PersistentList

import util

class WatchList:
    """ mix-in class for watchlist handling """

    security = ClassSecurityInfo()

    def wl_init(self):
        self._watchers = PersistentList()

    security.declareProtected(CMFCorePermissions.View, 'wl_getMode')
    def wl_getMode(self):
        """ return watchlist mode """
        self.watchlist_mode

    security.declareProtected(CMFCorePermissions.View, 'wl_getWatchers')
    def wl_getWatchers(self):
        """ return list of watchers """
        return self._watchers

    security.declareProtected(CMFCorePermissions.View, 'wl_isWatcher')
    def wl_isWatcher(self, email):
        """ is watcher """
        if email is None: return 0
        return email.lower() in self._watchers

    security.declareProtected(CMFCorePermissions.View, 'wl_addWatcher')
    def wl_addWatcher(self, email, RESPONSE):
        """ add watcher """
        if self.wl_isWatcher(email):
            raise RuntimeError('Email address %s already registered' % email)
        self._watchers.append(email.lower())
        util.redirect(RESPONSE, 'pcng_issue_view', 'You were added to the watchlist')

    security.declareProtected(CMFCorePermissions.View, 'wl_removeWatcher')
    def wl_removeWatcher(self, email, RESPONSE):
        """ remove watcher """
        if not self.wl_isWatcher(email):
            raise RuntimeError('Email address %s is not registered' % email)
        self._watchers.remove(email.lower())
        util.redirect(RESPONSE, 'pcng_issue_view', 'You were removed from the watchlist')

InitializeClass(WatchList)
