""" return the encoding of the plone site """
enc = context.portal_properties.site_properties.default_charset
if enc.lower() == 'utf8':
    enc = 'utf-8'
return enc
