
# Format the issue for email notification

def nl(text=''):
    l.append(text)

import DateTime

l = []

nl('Ticket #%s: %s' % (context.getId(), context.Title()))
nl('Betreff: %s' % (context.topic))
nl('Status: %s, Wichtigkeit: %s' % (context.status(), context.importance))
nl('Ticket URL: http://%s/%s' % (context.aq_parent.canonical_hostname, context.absolute_url(1)))
nl('-'*75 + '\n') 

n = 0
groups = context.getTranscript().getEventsGrouped()
for group in groups:
    datestr = context.toPortalTime(DateTime.DateTime(group[0].created), long_format=1)
    uid = group[0].user
    nl('#%d %s (%s) ----------------------------' % (len(groups)-n, datestr, uid)) 
    for ev in group:
        if ev.type == 'comment':
            nl('Kommentar:')
            nl(ev.comment)
        elif ev.type == 'action':
            nl('Aktion: %s"' % ev.action)
        elif ev.type == 'change':
            nl('Ge�ndert: %s: "%s" -> "%s"' % (ev.field, ev.old, ev.new))
        elif ev.type == 'incrementalchange':
            nl('Ge�ndert: %s: added: %s , removed: %s' % (ev.field, ev.added, ev.removed))
        elif ev.type == 'reference':
            nl('Referenz: %s: %s/%s (%s)' % (ev.tracker, ev.ticketnum, ev.comment))
        elif ev.type == 'upload':
            nl('Upload: %s: %s (%s)' % (ev.fieldid, ev.comment))
        else: 
            nl(str(ev))

    n+=1; nl()

return '\n'.join(l), 'iso-8859-15'
                                     

