"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Translateable.py,v 1.1 2003/10/19 12:55:45 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from config import i18n_domain
from Products.CMFPlone.PloneUtilities import translate 

class Translateable:

    security = ClassSecurityInfo()

    security.declarePublic('translate')
    def translate(self, msg_id, text, **kw):

        prefered_language = 'de'  # this should be taken from the PLT

        ret = translate(domain=i18n_domain, 
                         msgid=msg_id, 
                         context=self,
                         target_language=prefered_language,
                         mapping=kw,  
                         default=text)

        return ret
            
InitializeClass(Translateable)


