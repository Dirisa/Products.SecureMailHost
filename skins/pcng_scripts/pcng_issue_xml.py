##parameters=preamble=1


# Export issue as XML
# Warning: the format might change in the future

import base64

l = []
enc = context.getSiteEncoding()
now = DateTime()

def w(t): l.append(t)

def convertValue(v):
    if same_type(v, ''):
        return 'string', unicode(v, enc, 'replace').encode('utf-8')
    elif same_type(v, 0):
        return 'int', str(v)
    elif same_type(v, u''):
        return 'string',  v.encode('utf-8')
    elif same_type(v, 0.0):
        return 'float', str(v)
    elif v is None:
        return 'null', ''
    elif same_type(v, now):
        return 'date-iso', v.ISO()
    elif same_type(v, []):
        return 'list', repr(v)
        
    else:
        raise RuntimeError('Unsupported type: %s' % v)

def vXML(v):
    if same_type(v, ''):
        w('\t\t<value type="string">%s</value>' % unicode(v, enc, 'replace').encode('utf-8'))
    elif same_type(v, 0):
        w('\t\t<value type="int">%s</value>' % str(v))
    elif same_type(v, u''):
        w('\t\t<value type="string">%s</value>' % v.encode('utf-8'))
    elif same_type(v, 0.0):
        w('\t\t<value type="float">%s</value>' % str(v))
    elif v is None:
        w('\t\t<value type="null"></value>')
    elif same_type(v, now):
        w('\t\t<value type="date-iso">%s</value>' % v.ISO())
    elif same_type(v, []):
        w('\t\t<value type="list">%s</value>' % repr(v))
        
    else:
        raise RuntimeError('Unsupported type: %s' % v)

if preamble:
    w('<?xml version="1.0" encoding="utf-8"?>')


w('<issue id="%s" collector="%s">' % (context.getId(), context.aq_parent.getId()))

################################################################
# Metadata
################################################################

w('<metadata>')
for f in context.Schema().fields():
    v = f.get(context)
    if same_type(v, []) or same_type(v, ()):
        w('\t<field name="%s">' % str(f.getName()))
        w('\t\t<list>')
        for item in v:
            type, value = convertValue(item)
            w('\t\t\t<value type="%s">%s</field>' % (type, value))
        w('\t\t</list>')
        w('\t</field>')
    else:
        type, value = convertValue(v)
        w('\t<field name="%s" type="%s">%s</field>' % (str(f.getName()), type, value))
w('</metadata>')

################################################################
# Transcript
################################################################

w('<transcript>')
for e in context.getTranscript().getEvents():
    w('\t<entry type="%s" timestamp="%s">' % (e.getType(), DateTime(e.getTimestamp()).ISO()) )
    if e.type == 'comment':
        w('\t\t<comment>')
        vXML((e.comment))
        w('\t\t</comment>')
    elif e.type == 'change':
        w('\t\t<field name="%s">' % e.field)
        w('\t\t\t<old>') 
        vXML(e.old)
        w('\t\t\t</old>')
        w('\t\t\t<new>')
        vXML(e.new)
        w('\t\t\t</new>')
        w('\t\t</field>')

    elif e.type == 'incrementalchange':
        w('\t\t<field name="%s">' % repr(e.field))
#        w('<added>'); vXML(e.added); w('</added>')
#        w('<removed>'); vXML(e.removed); w('</removed>')
        w('\t\t</field>')


    elif e.type == 'reference':
       w('\t\t<reference id="%s" collector="%s">' % (e.ticketnum, e.tracker))
       w('<comment>')
       vXML(e.comment)
       w('</comment>')
       w('\t\t</reference>') 

    elif e.type == 'upload':
        o = getattr(context, e.fileid)

        w('\t\t<upload id="%s" mimetype="%s">' % (o.getId(), o.content_type))
        w('\t\t\t<data>')
        w(base64.encodestring(str(o.data)))
        w('\t\t\t</data>')

        type, value = convertValue(e.comment)
        
        w('\t\t\t<comment type="%s">%s</comment>' % (type, value))
        w('\t\t</upload>')

    w('\t</entry>')

w('</transcript>')
    

w('</issue>')

return '\n'.join(l)

