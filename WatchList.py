"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: WatchList.py,v 1.11 2004/11/12 15:37:52 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import  ClassSecurityInfo 
from Products.CMFCore.CMFCorePermissions import *
from ZODB.PersistentList import PersistentList

import util

class WatchList:
    """ mix-in class for watchlist handling """

    security = ClassSecurityInfo()

    def wl_init(self):
        self._watchers = PersistentList()

    security.declareProtected(View, 'wl_getMode')
    def wl_getMode(self):
        """ return watchlist mode """
        return self.watchlist_mode

    security.declareProtected(View, 'wl_getWatchers')
    def wl_getWatchers(self):
        """ return list of watchers """
        return self._watchers

    security.declareProtected(View, 'wl_isWatcher')
    def wl_isWatcher(self, email):
        """ is watcher """
        if email is None: return 0
        return email.lower() in self._watchers

    security.declareProtected(View, 'wl_addWatcher')
    def wl_addWatcher(self, email, RESPONSE):
        """ add watcher """
        if self.wl_isWatcher(email):
            raise RuntimeError(self.Translate('email_already_registered', 'Email address $email already registered', email=email))
        self._watchers.append(email.lower())
        util.redirect(RESPONSE, 'pcng_issue_view', 
                      self.Translate('watchlist_added', 'You were added to the watchlist'))

    security.declareProtected(View, 'wl_removeWatcher')
    def wl_removeWatcher(self, email, RESPONSE):
        """ remove watcher """
        if not self.wl_isWatcher(email):
            raise RuntimeError(self.Translate('email_not_registered', 'Email address $email not registered', email=email))
        self._watchers.remove(email.lower())
        util.redirect(RESPONSE, 'pcng_issue_view', 
                      self.Translate('watchlist_removed', 'You were removed from the watchlist'))

InitializeClass(WatchList)
