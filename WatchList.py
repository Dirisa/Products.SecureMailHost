"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: WatchList.py,v 1.1 2003/09/08 04:04:45 ajung Exp $
"""

class WatchList:
    """ mix-in class for watchlist handling """

    def wl_init(self):
        self._watchers = []

    def wl_getWatchers(self):
        return self._watchers

    def wl_isWatcher(self, email):
        return email.lower() in self._watchers

    def wl_addWatcher(self, email):
        if self.wl_isWatcher(email):
            raise RuntimeError('Email address %s already registered' % email)
        self._watchers.append(email.lower())

    def wl_removeWatcher(self, email):
        if not self.wl_isWatcher(email):
            raise RuntimeError('Email address %s is not registered' % email)
        self._watchers.remove(email.lower())

InitializeClass(WatchList)
