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
nl('%s: %s' % (TR('created_by', 'Created by'), context.Creator()))
nl('-'*75 + '\n') 

nl(context.Translate('label_description', 'Description') + ":")
nl('-'*40)
nl(context.wrap_text(context.Description()))
nl()


# Comments
n = 0
events = context.getTranscript().getEvents(types=('comment', 'upload', 'reference'))
for event in events:
    datestr = context.toLocalizedTime(DateTime.DateTime(event.getCreated()), long_format=1)
    creator = event.getCreator()
    user = event.getUser()

    nl('#%d %s %s (%s)' % (len(events)-n, TR(event.getType(), event.getType()), datestr, creator)) 
    nl('-'*75)
    nl(context.pcng_format_event(event, 'plain'))
    n+=1; nl()
nl()


# metadata
nl(TR('metadata', 'Metadata'))    
nl('-'*75 + '\n') 
events = context.getTranscript().getEvents()
events = [e for e in events  if e.getType() not in ('comment', 'upload', 'reference')]
for event in events:
    date = event.getCreated()
    date = context.toLocalizedTime(DateTime.DateTime(date), long_format=1)
    type = event.getType()
    user = event.getCreator()
    try:
        field = event.getField()
    except: 
        field = ''
    text = context.pcng_format_event(event, 'plain')

    s = '%s | %10s | %10s | %10s | %s' % (date, type, user, field, text)
    nl(s)
nl()


# references
if context.haveATReferences():
    events = context.getTranscript().getEvents(types=('references'))
    if events:
        nl(TR('references_to_other_issues', 'References to other issues'))
        nl('-'*40)
        for event in events:
            text = context.pcng_format_event(event, 'plain')
            nl('   -> http://%s/%s' % (context.aq_parent.canonical_hostname, text))
        nl()


# Uploads
events = context.getTranscript().getEvents(types=('upload'))
if events:
    nl(TR('uploads', 'Uploads'))
    nl('-'*40)
    for event in events:
        nl('   -> %s/%s' % (context.absolute_url(), event.getFileId()))

return '\n'.join(l)
