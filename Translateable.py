"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Translateable.py,v 1.5 2003/10/19 16:17:23 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from config import i18n_domain

class Translateable:
    """ Mix-in class to provide i18n support for FS-based code """

    security = ClassSecurityInfo()

    security.declarePublic('translate')
    def translate(self, msg_id, text, **kw):
        """ ATT: this code is subject to change """

        pts = getattr(self, '_v_have_pts', None)
        if pts is None:

            try:
                pts = self.Control_Panel.TranslationService
                self._v_have_pts = pts
            except:
                self._v_have_pts = None
                return self._interpolate(text, kw)

            if pts .meta_type.find('Broken') > -1: 
                self._v_have_pts = None
                return self._interpolate(text, kw)

        ret = pts.translate(domain=i18n_domain, 
                            msgid=msg_id, 
                            context=self,
                            mapping=kw,  
                            default=text)
        return ret

    def _interpolate(self, text, mapping):
        """ convert a string containing vars for interpolation ('$var')
            with the corresponding value from the mapping.
        """ 
        for k,v in mapping.items():
            text = text.replace('$%s' % k, str(v))
        return text
            
InitializeClass(Translateable)


