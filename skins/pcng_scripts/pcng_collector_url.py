# Return absolute URL of the collector in the context of the collector
# or an issue

if context.meta_type == 'PloneIssueNG':
    return context.aq_parent.absolute_url()
if context.meta_type == 'PloneCollectorNG':
    return context.absolute_url()
else:
    raise ValueError('Unkown type: %s' % context.meta_type)

