##parameters=s

# Convert a string using the site-encodings

enc = here.getSiteEncoding()
if same_type(s, u''):
    return s.encode(enc)
else:
    return unicode(s, enc, 'replace').encode(enc)
