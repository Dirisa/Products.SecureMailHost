"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Translateable.py,v 1.2 2003/10/19 14:00:11 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from config import i18n_domain

try:
    from Products.CMFPlone.PloneUtilities import translate 
    have_ts = 1
except ImportError:
    have_ts = 0

class Translateable:

    security = ClassSecurityInfo()

    security.declarePublic('translate')
    def translate(self, msg_id, text, **kw):
        if not have_ts: return text % kw

        prefered_language = 'de'  # this should be taken from the PLT

        ret = translate(domain=i18n_domain, 
                         msgid=msg_id, 
                         context=self,
                         target_language=prefered_language,
                         mapping=kw,  
                         default=text)
        return ret
            
InitializeClass(Translateable)


