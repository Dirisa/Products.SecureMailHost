##parameters=e, format='plain'

# Format an Event instance 'e' from Transcript2.py 

def preXML(e):
    return '<%s creator="%s" user="%s" public="%s" created="%s">' % \
        (e.getType(), e.Creator(), e.getUser(), e.isPublic(), e.created())

def postXML(e):
    return '</%s>' % e.getType()

type = e.getType()
TR = context.Translate
site_encoding = context.getSiteEncoding()

if type == 'comment':

    if format == 'plain':
        s = '%s: %s' % (TR(type, type, as_unicode=1), e.getComment())
        return s

    elif format == 'html':
        s = '<pre>%s</pre>' % context.wrap_text(e.getComment(), 80, reencode=False)
        return s

    elif format == 'pdf':
        s = '<b>%s</b>: %s' % (TR(type, type, as_unicode=1), e.getComment())
        return s

    elif format == 'xml':
        xml = preXML(e)
        xml += postXML(e)
        return xml

    else:
        raise ValueError('Unknown format: %s' % format)

elif type == 'change':
    if e.getOld() == e.getNew(): return ''

    if format == 'plain':
        s = '%s: %s -> %s' % (e.getField(), e.getOld(), e.getNew())
        return s

    elif format == 'html':
        s = '%s -> %s' % (e.getOld(), e.getNew())
        return s

    elif format == 'pdf':
        s = '<b>%s</b>: %s -> %s' % (e.getField(), e.getOld(), e.getNew())
        return s

    elif format == 'xml':
        xml = preXML(e)
        xml += postXML(e)
        return xml

    else:
        raise ValueError('Unknown format: %s' % format)

elif type == 'incremental':
    if e.getAdded() == e.getRemoved(): return ''

    if format == 'plain':
        s = '%s: -%s, +%s' % (e.getField(), e.getRemoved(), e.getAdded())
        return s

    elif format == 'html':
        s = '- %s, + %s' % (e.getRemoved(), e.getAdded())
        return s

    elif format == 'pdf':
        s = '<b>%s</b>: -%s, +%s' % (e.getField(), e.getRemoved(), e.getAdded())
        return s

    elif format == 'xml':
        xml = preXML(e)
        xml += postXML(e)
        return xml

elif type == 'upload':

    if format == 'plain':
        s = '%s: %s (%s)' % (TR('upload','Upload'), e.getFileId(), e.getComment())
        return s

    elif format == 'html':
        s = '<a href="%s">%s</a>:</span> %s' % (e.getFileId(), e.getFileId(), e.getComment())
        return s

    elif format == 'pdf':
        s = '<b>%s</b>: %s (%s)' % (TR('upload', 'Upload'), e.getFileId(), e.getComment())
        return s

    elif format == 'xml':
        xml = preXML(e)
        xml += postXML(e)
        return xml

elif type == 'reference':

    if format == 'plain':
        s = '%s: %s/%s - %s' % (TR('reference', 'Reference'), e.getTrackerId(), e.getIssueId(), e.getComment())
        return s

    elif format == 'html':
        s = '<a href="/%s">%s/%s</a> - %s' % (e.getIssueURL(),  e.getTrackerId(), e.getIssueId(), e.getComment())
        return s

    elif format == 'pdf':
        s = '<b>%s</b>: %s/%s - %s' % (TR('reference', 'Reference'), e.getTrackerId(), e.getIssueId(), e.getComment())
        return s

    elif format == 'xml':
        xml = preXML(e)
        xml += postXML(e)
        return xml

elif type == 'action':
    return e.getAction()

else:
    raise ValueError('Unknown type: %s' % type)
