##parameters=s,enc='iso-8859-1'

# Convert a string using the site-encodings

site_enc = here.getSiteEncoding()

if same_type(s, u''):
    return s.encode(site_enc)
else:
    return unicode(s, enc, 'replace').encode(site_enc)
