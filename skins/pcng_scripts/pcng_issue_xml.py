##parameters=preamble=1


# Export issue as XML
# Warning: the format might change in the future

l = []
enc = context.getSiteEncoding()
now = DateTime()

def w(t): l.append(t)

def vXML(v):
    if same_type(v, ''):
        w('<value type="string">%s</value>' % unicode(v, enc, 'replace').encode('utf-8'))
    elif same_type(v, 0):
        w('<value type="int">%s</value>' % str(v))
    elif same_type(v, u''):
        w('<value type="string">%s</value>' % v.encode('utf-8'))
    elif same_type(v, 0.0):
        w('<value type="float">%s</value>' % str(v))
    elif v is None:
        w('<value type="null"></value>')
    elif same_type(v, now):
        w('<value type="date-iso">%s</value>' % v.ISO())
    elif same_type(v, []):
        w('<value type="list-iso">%s</value>' % repr(v))
        
    else:
        raise RuntimeError('Unsupported type: %s' % v)

if preamble:
    w('<?xml version="1.0" encoding="utf-8"?>')


w('<issue id="%s" collector="%s">' % (context.getId(), context.aq_parent.getId()))
for f in context.Schema().fields():
    v = f.get(context)
    w('<field name="%s">' % f.getName())
    if same_type(v, []) or same_type(v, ()):
        w('<list>')
        for item in v: vXML(item)
        w('</list>')
    else:
        vXML(v)
    w('</field>')

w('<transcript>')

for e in context.getTranscript().getEvents():
    w('<entry type="%s" timestamp="%s">' % (e.getType(), DateTime(e.getTimestamp()).ISO()) )
    if e.type == 'comment':
        w('<comment>')
        vXML((e.comment))
        w('</comment>')
    elif e.type == 'change':
        w('<field name="%s">' % e.field)
        w('<old>'); vXML(e.old); w('</old>')
        w('<new>'); vXML(e.new); w('</new>')
        w('</field>')

    elif e.type == 'incrementalchange':
        w('<field name="%s">' % repr(e.field))
#        w('<added>'); vXML(e.added); w('</added>')
#        w('<removed>'); vXML(e.removed); w('</removed>')
        w('</field>')


    elif e.type == 'reference':
       w('<reference id="%s" collector="%s">' % (e.ticketnum, e.tracker))
       w('<comment>')
       vXML(e.comment)
       w('</comment>')
       w('</reference>') 

    elif e.type == 'upload':
        w('<upload id="%s">' % e.fileid)
        w('<comment>')
        vXML((e.comment))
        w('</comment>')
        w('</upload>')

    w('</entry>')

w('</transcript>')
    

w('</issue>')

return '\n'.join(l)

