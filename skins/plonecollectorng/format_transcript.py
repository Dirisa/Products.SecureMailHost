##parameters=language=None

# Format the issue for email notification.
# The return format is UNICODE !

import DateTime
from textwrap import wrap

# Wrapper for translate()
def TR(id, default):
    return context.Translate(id, default, language, as_unicode=1)

# convert string to unicode and append to list
def nl(text=''):
    if same_type(text, u''):
        l.append(text)
    else:
        l.append(unicode(text, site_encoding))

l = []

# Determine site encoding
site_encoding = context.getSiteEncoding()

nl('='*79)
nl('= %s' % context.Translate('dont_remove_information_below', "Don't remove this information block if replying to this message"))
for line in context.getEncryptedInformations().strip().split('\n'):
    nl('=> %s' % line)
nl('='*79)
nl('')

s= '%s: #%s: %s, ' % (TR('Issue', 'Issue'), context.getId(), unicode(context.Title(), site_encoding))
s+='%s: %s, ' % (TR('topic', 'Topic'),context.topic)
s+='%s: %s, %s: %s, %s: %s' % (TR('status', 'Status'), TR(context.status(), context.status()), 
                               TR('importance','Importance'), TR(context.importance, context.importance), 
                               TR('classification', 'Classification'), context.classification)
nl(s)
nl('%s URL: http://%s/%s' % (TR('Issue', 'Issue'), context.aq_parent.canonical_hostname, context.absolute_url(1)))
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
        
    nl('#%d %s %s (%s) ----------------------------' % (len(groups)-n, TR(action, action), datestr, uid)) 

    for ev in group:

        if ev.type == 'comment':
            nl('%s:' % TR('comment', 'Comment'))
            nl(context.wrap_text(ev.comment,indent=4))

        elif ev.type == 'change':
            nl(u'%s: %s: "%s" -> "%s"' % (TR('Change', 'Change'), ev.field, ev.old, ev.new))

        elif ev.type == 'incrementalchange':
            nl(u'%s: %s: %s: %s , %s: %s' % (TR('changed', 'Changed'), ev.field, 
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
                                     
