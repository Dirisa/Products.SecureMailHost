##parameters=issuenumber

# Jump to the view method of an issue given by its number

issuenumber = issuenumber.strip()
if hasattr(context, issuenumber):
    if context.meta_type == 'PloneIssueNG':
        url = "%s/%s" % (context.aq_parent.absolute_url(), issuenumber)
    else:
        url = "%s/%s" % (context.absolute_url(), issuenumber)
    context.REQUEST.RESPONSE.redirect(url)
else:
    context.REQUEST.RESPONSE.redirect(context.absolute_url() + "/base_view?portal_status_message=%s" % 
        context.Translate('no_such_issue', 'No such issue'))

