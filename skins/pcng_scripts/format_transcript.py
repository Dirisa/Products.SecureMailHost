##parameters=language=None

# Format the issue for email notification.
# The return format is UNICODE !

import DateTime

# Wrapper for translate()
def TR(id, default):
    return context.Translate(id, default, language, as_unicode=1)


def getValue(fieldname, translate=0):

    vocab = context.pcng_vocabulary_values(fieldname)
    v = context.Schema()[fieldname].getAccessor(context)()

    if translate:
        v = str(v)
        return TR(vocab.get(v, v), vocab.get(v,v))
    else:
        if same_type(v, []):
            return ', '.join([vocab.get(item, item) for item in v])
        else:
            return vocab.get(v, v)

# convert string to unicode and append to list
def nl(text=None):
    if text == '': return
    if text is None: 
        l.append(u'')
        return
    if same_type(text, u''):
        l.append(text)
    else:
        l.append(unicode(text, site_encoding))

l = []

# Determine site encoding
site_encoding = context.getSiteEncoding()

schema = context.Schema()
mode = context.getIssue_email_submission()

if mode != 'disabled':
    nl('='*80)
    nl(TR('followup_help1', 'If you reply to this notification email, please do not include this text in the'))
    nl(TR('followup_help2', 'reply.  In addition you must attach the attached file "pcng.key" in your reply.'))
    nl(TR('followup_help3', 'Otherwise your reply can not be processed. Thank you.'))
    nl('='*80)
    nl()    

s= '%s: #%s: %s, ' % (TR('Issue', 'Issue'), context.getId(), unicode(context.Title(), site_encoding))
s+='%s: %s, ' % (TR('topic', 'Topic'), context.topic)

s+='%s: %s, %s: %s, %s: %s' % (TR('status', 'Status'), TR(context.status(), context.status()), 
                               TR('importance','Importance'), getValue('importance'),
                               TR('classification', 'Classification'), getValue('classification'))

nl(s)
nl('%s URL: http://%s/%s' % (TR('Issue', 'Issue'), context.aq_parent.canonical_hostname, context.absolute_url(1)))
nl('-'*75 + '\n') 

nl(context.Translate('label_description', 'Description') + ":")
nl('-'*40)
nl(context.wrap_text(context.Description()))

nl()

n = 0
groups = context.getTranscript().getEventsGrouped()
for group in groups:
    datestr = context.toLocalizedTime(DateTime.DateTime(group[0].created()), long_format=1)
    creator = group[0].Creator()
    user = group[0].getUser()

    # Find action in current group
    action = context.pcng_action_from_events(group)
    nl('#%d %s %s (%s)' % (len(groups)-n, TR(action, action), datestr, creator)) 
    nl('-'*75)

    for ev in group:
        if ev.getType() == 'action': continue
        nl(context.pcng_format_event(ev, 'plain'))

    n+=1; nl()


if context.haveATReferences():
    refs = context.getForwardReferences()
    if refs:
        nl(TR('references_to_other_issues', 'References to other issues'))
        nl('-'*40)
        for r in refs:
            target = r.getTargetObject()
            nl('   -> http://%s/%s' % (context.aq_parent.canonical_hostname, target.absolute_url(1)))

return '\n'.join(l)
                                     
