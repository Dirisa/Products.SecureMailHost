"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: Translateable.py,v 1.38 2004/11/12 15:37:52 ajung Exp $
"""

from types import UnicodeType, StringType

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

try:
    from Products.PlacelessTranslationService import getTranslationService
except ImportError:
    from zLOG import LOG, WARNING
    LOG('plonecollectorng', WARNING, 'PlacelessTranslationService not found (required for running PloneCollectorNG')
    import os
    os._exit(1)

from config import i18n_domain

class Translateable:
    """ Mix-in class to provide i18n support for FS-based code """

    security = ClassSecurityInfo()

    def _getPloneEncoding(self):
        """ return the site encoding of Plone """
        encoding = getattr(self, '_v_site_encoding', None)
        if encoding is None:
            self._v_site_encoding = self.portal_properties.site_properties.default_charset
        return self._v_site_encoding    

    def _unicode(self, s, encoding=None):
        try:
            return unicode(s, encoding)
        except:
            try:
                return unicode(s, self._getPloneEncoding())
            except:
                try:
                    return unicode(s, 'latin1')
                except:
                    pass

    security.declarePublic('translate')
    def Translate(self, msgid, text, target_language=None, as_unicode=0, **kw):
        """ utranslate() wrapper """
        
        pts = getTranslationService()

        # Workaround for mega-kaputt context.REQUEST which turns out to be
        # not a REQUEST-like object but some unknown acquisition shit.
        if isinstance(self.REQUEST, StringType): pts = None

        if pts is None:
            r = self._interpolate(text, kw)
            if as_unicode:
                if isinstance(r, UnicodeType):
                    return r
                else:
                    return unicode(r, self._getPloneEncoding())
            else: 
                return r

        v = pts.utranslate(domain=i18n_domain, 
                           msgid=msgid, 
                           context=self,
                           mapping=kw,  
                           default=text,
                           target_language=target_language)
        if not v: 
            v = self._unicode(text)
        if isinstance(v, StringType):
            if as_unicode: return unicode(v, self._getPloneEncoding())
            else: return v
        else:
            if as_unicode: return v
            else: return v.encode(self._getPloneEncoding())
            

    security.declarePublic('getLanguages')
    def getLanguages(self):
        """ return the languages """
        pts = getTranslationService()
        return pts.getLanguages(i18n_domain)

    def _interpolate(self, text, mapping):
        """ convert a string containing vars for interpolation ('$var')
            with the corresponding value from the mapping.
        """ 
        for k,v in mapping.items():
            text = text.replace('$%s' % k, str(v))
        return text
            
InitializeClass(Translateable)

