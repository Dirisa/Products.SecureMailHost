##parameters=issuenumber

# Jump to the view method of an issue given by its number

issuenumber = issuenumber.strip()
if hasattr(context, issuenumber):
    url = "%s/%s" % (context.absolute_url(), issuenumber)
    context.REQUEST.RESPONSE.redirect(url)
else:
    raise ValueError('There is no issue #%s' % issuenumber)
