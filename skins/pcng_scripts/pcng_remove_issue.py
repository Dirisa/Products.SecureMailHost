##parameters=id

assert context.meta_type == 'PloneIssueNG'
collector = context.aq_parent
assert collector.meta_type == 'PloneCollectorNG'
collector.manage_delObjects([id])
msg = collector.Translate('issue_deleted', 'Issue deleted')
collector.REQUEST.RESPONSE.redirect(collector.absolute_url() + "/pcng_view?portal_status_message=%s" % msg)
