##parameters=language=None

# Format the issue for email notification.
# The return format is UNICODE !

import DateTime

# Wrapper for translate()
def TR(id, default):
    return context.translate(id, default, language)

# convert string to unicode and append to list
def nl(text=''):
    if same_type(text, u''):
        l.append(text)
    else:
        l.append(unicode(text, site_encoding))

# a simple indenter for text blocks
def indent_block(text):
    return '\n'.join(['    %s' % line    for line in text.split('\n')])

l = []

# Determine site encoding
site_encoding = context.getSiteEncoding()

nl('%s: #%s: %s' % (TR('issue', 'Issue'), context.getId(), context.Title()))
nl('%s: %s' % (TR('topic', 'Topic'),context.topic))
nl('%s: %s, %s: %s, %s: %s' % (TR('status', 'Status'), context.status(), 
                               TR('importance','Importance'), context.importance, 
                               TR('classification', 'Classification'), context.classification))
nl('%s URL: http://%s/%s' % (TR('issue', 'Issue'), context.aq_parent.canonical_hostname, context.absolute_url(1)))
nl('-'*75 + '\n') 

n = 0
groups = context.getTranscript().getEventsGrouped()
for group in groups:
    datestr = context.toLocalizedTime(DateTime.DateTime(group[0].created), long_format=1)
    uid = group[0].user

    # Find action in current group
    action = ''
    for ev in group:
        if ev.type == 'action': action = ev.action
        
    nl('#%d %s %s (%s) ----------------------------' % (len(groups)-n, action, datestr, uid)) 

    for ev in group:

        if ev.type == 'comment':
            nl('%s:' % TR('comment', 'Comment'))
            nl(indent_block(ev.comment))

        elif ev.type == 'change':
            nl('%s: %s: "%s" -> "%s"' % (TR('change', 'Change'), ev.field, ev.old, ev.new))

        elif ev.type == 'incrementalchange':
            nl('%s: %s: %s: %s , %s: %s' % (TR('changed', 'Changed'), ev.field, 
                                            TR('added', 'Added'), ev.added, 
                                            TR('removed', 'Removed'), ev.removed))
        elif ev.type == 'reference':
            nl('%s: %s: %s/%s (%s)' % (TR('reference', 'Reference'), ev.tracker, ev.ticketnum, ev.comment))

        elif ev.type == 'upload':
            s = '%s: %s/%s ' % (TR('upload', 'Upload'), context.absolute_url(), ev.fileid)
            if ev.comment:
                s+= ' (%s)' % ev.comment
            nl(s)

    n+=1; nl()

return '\n'.join(l)
                                     
