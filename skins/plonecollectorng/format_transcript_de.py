
# Format the issue for email notification

def nl(text=''):
    l.append(text)

def indent_block(text):
    return '\n'.join(['    %s' % line    for line in text.split('\n')])

import DateTime

l = []

nl('Ticket #%s: %s' % (context.getId(), context.Title()))
nl('Betreff: %s' % (context.topic))
nl('Status: %s, Dringlichkeit: %s, Klassifizierung: %s' % (context.status(), context.importance, context.classification))
nl('Ticket URL: http://%s/%s' % (context.aq_parent.canonical_hostname, context.absolute_url(1)))
nl('-'*75 + '\n') 

n = 0
groups = context.getTranscript().getEventsGrouped()
for group in groups:
    datestr = context.toPortalTime(DateTime.DateTime(group[0].created), long_format=1)
    uid = group[0].user
    nl('#%d %s %s (%s) ----------------------------' % (len(groups)-n, context.lastAction().capitalize(), datestr, uid)) 
    for ev in group:
        if ev.type == 'comment':
            nl('Kommentar:')
            nl(indent_block(ev.comment))
        elif ev.type == 'change':
            nl('Geändert: %s: "%s" -> "%s"' % (ev.field, ev.old, ev.new))
        elif ev.type == 'incrementalchange':
            nl('Geändert: %s: added: %s , removed: %s' % (ev.field, ev.added, ev.removed))
        elif ev.type == 'reference':
            nl('Referenz: %s: %s/%s (%s)' % (ev.tracker, ev.ticketnum, ev.comment))
        elif ev.type == 'upload':
            s = 'Upload: %s/%s ' % (context.absolute_url(), ev.fileid)
            if ev.comment:
                s+= ' (%s)' % ev.comment
            nl(s)
        else: 
            raise TypeError('Unhandled event: %s' % repr(ev))

    n+=1; nl()

return '\n'.join(l), 'iso-8859-15'
                                     

