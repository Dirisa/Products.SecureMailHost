"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Translateable.py,v 1.3 2003/10/19 15:07:47 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from config import i18n_domain

try:
    from Products.CMFPlone.PloneUtilities import translate 
    have_ts = 1
except ImportError:
    have_ts = 0

class Translateable:
    """ Mix-in class to provide i18n support for FS-based code """

    security = ClassSecurityInfo()

    security.declarePublic('translate')
    def translate(self, msg_id, text, **kw):
        """ ATT: this code is subject to change """a

        if not have_ts: return text % kw

        PL = getToolByName(self, 'portal_languages', None)
        if PL:
            prefered_lang = self.portal_languages.getRequestLanguages()[0]
        else:
            prefered_lang = 'en'

        ret = translate(domain=i18n_domain, 
                         msgid=msg_id, 
                         context=self,
                         target_language=prefered_lang,
                         mapping=kw,  
                         default=text)
        return ret
            
InitializeClass(Translateable)


