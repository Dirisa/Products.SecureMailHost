"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Translateable.py,v 1.19 2004/01/30 15:55:52 ajung Exp $
"""

from types import UnicodeType, StringType

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from config import i18n_domain

class Translateable:
    """ Mix-in class to provide i18n support for FS-based code """

    security = ClassSecurityInfo()

    def _getPTS(self):
        """ return PTS instance """

        pts = getattr(self, '_v_have_pts', None)
        if pts is None:
            try:
                pts = self.Control_Panel.TranslationService
                self._v_have_pts = pts
            except:
                self._v_have_pts = None

        try:
            self._v_have_pts.translate
            return self._v_have_pts
        except:
            return None

    def _getPloneEncoding(self):
        """ return the site encoding of Plone """
        encoding = getattr(self, '_v_site_encoding', None)
        if encoding is None:
            self._v_site_encoding = self.portal_properties.site_properties.default_charset
        return self._v_site_encoding    


    security.declarePublic('translate')
    def translate(self, msgid, text, target_language=None, as_unicode=0, **kw):
        """ ATT: this code is subject to change """

        
        pts = self._getPTS()
        if pts is None:
            r = self._interpolate(text, kw)
            if as_unicode:
                return unicode(r, self._getPloneEncoding())
            else: 
                return r

        # Using the as_unicode parameter requires the lastest PTS version
        # from the CVS. In generell we retrieve the translations from PTS
        # always as unicode and convert it back to the Plone site encoding
        # if necessary

        v = pts.translate(domain=i18n_domain, 
                            msgid=msgid, 
                            context=self,
                            mapping=kw,  
                            default=text,
                            target_language=target_language,
                            as_unicode=1)
        
        if not v: v = u''
        if isinstance(v, StringType):
            if as_unicode: return unicode(v, self._getPloneEncoding())
            else: return v
        else:
            if as_unicode: return v
            else: return v.encode(self._getPloneEncoding())
            

    security.declarePublic('getLanguages')
    def getLanguages(self):
        """ return the languages """
        pts = self._getPTS()
        if pts:
            return pts.getLanguages(i18n_domain)
        else:
            return []

    def _interpolate(self, text, mapping):
        """ convert a string containing vars for interpolation ('$var')
            with the corresponding value from the mapping.
        """ 
        for k,v in mapping.items():
            text = text.replace('$%s' % k, str(v))
        return text
            
InitializeClass(Translateable)


