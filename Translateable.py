"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Translateable.py,v 1.7 2003/11/01 17:03:26 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from config import i18n_domain

class Translateable:
    """ Mix-in class to provide i18n support for FS-based code """

    security = ClassSecurityInfo()

    security.declarePublic('translate')
    def translate(self, msgid, text, **kw):
        """ ATT: this code is subject to change """

        pts = getattr(self, '_v_have_pts', None)
        if pts is None:

            try:
                pts = self.Control_Panel.TranslationService
                self._v_have_pts = pts
            except:
                self._v_have_pts = None
                return self._interpolate(text, kw)

            if pts.meta_type.find('Broken') > -1: 
                self._v_have_pts = None
                return self._interpolate(text, kw)

        ret = pts.translate(domain=i18n_domain, 
                            msgid=msgid, 
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


