"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: pdfwriter.py,v 1.8 2003/11/16 17:48:21 ajung Exp $
"""

import os, sys, cStringIO, tempfile

try:
    from PIL import Image as PIL_Image
    have_pil = 1
except ImportError: have_pil = 0

from DateTime import DateTime

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch


styles = getSampleStyleSheet()

PAGE_HEIGHT = defaultPageSize[1]

def myLaterPages(canvas, doc):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(66,45,66,PAGE_HEIGHT-45)
    canvas.line(66,PAGE_HEIGHT-70, 555, PAGE_HEIGHT-70)
    canvas.setFont('Helvetica-Bold',15)
    canvas.drawString(inch, PAGE_HEIGHT-62, doc.collector_title)
    canvas.setFont('Helvetica',11)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.drawString(450, 0.75 * inch, doc.collector.toPortalTime(DateTime(), long_format=1))
    canvas.restoreState()

myFirstPage = myLaterPages

Elements = []

HeaderStyle = styles["Heading3"] 
HeaderStyle.defaults['fontName'] = 'Helvetica'

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.05):
    txt = '<font face="helvetica">%s</font>' % txt
    p = XPreformatted(txt, style)
    Elements.append(p)

ParaStyle = styles["Normal"]
ParaStyle.defaults['fontName'] = 'Helvetica'

def p(txt):
    txt = '<font face="helvetica">%s</font>' % txt
    return header(txt, style=ParaStyle, sep=0.0)

PreStyle = styles["Code"]

def pre(txt):
    p = Preformatted(txt, PreStyle)
    Elements.append(p)

DefStyle = styles["Definition"]

def definition(txt):
    txt = '<font face="helvetica">%s</font>' % txt
    p = XPreformatted(txt, DefStyle)
    Elements.append(p)


def pdfwriter(collector, ids):

    tempfiles = []

    for issue_id in ids:
        issue = getattr(collector, str(issue_id))

        header('Issue #%s' % issue.title_or_id())

        header("Description")
        definition(issue.description)

        if issue.solution:
            header("Solution")
            definition(issue.solution)

        for name in issue.schema_getNames():
            if name in ('default', 'metadata'): continue
            
            l =[]

            for field in issue.schema_getSchema(name).fields():
                if field.getName() in ('description', 'title'): continue

                value = issue.getParameter(field.getName())

                if hasattr(field, 'vocabulary'):
                    vocab = field.Vocabulary(issue)
                    v = issue.displayValue(vocab, value)
                else:
                    v = value

                if v:
                    l.append('<b>%s</b>: %s ' % (field.widget.Label(issue), v))

            s = (', '.join(l)).strip()
            if s:
                header(name.capitalize())
                definition(s)

        for img in issue.objectValues('Portal Image'):

            if have_pil:
                fname = tempfile.mktemp() + img.getId()
                tempfiles.append(fname)
                open(fname, 'w').write(str(img.data))
                image = PIL_Image.open(fname)
                width, height= image.size
                ratio = width*1.0 / height

                max = 4*inch
                if ratio > 1.0:
                    width = max
                    height = max / ratio
                else:
                    height = max
                    width = max / ratio

                Elements.append(Image(fname, width, height))
                Elements.append(Spacer(100, 0.2*inch))

            else:
                p('Image: %s' % img.title_or_id())

        header('Transcript')

        groups = issue.getTranscript().getEventsGrouped(reverse=0)
        n = 1
        for group in groups:
            datestr = issue.toPortalTime(DateTime(group[0].created), long_format=1)
            uid = group[0].user
            header('#%d %s %s (%s)' % (n, issue.lastAction().capitalize(), datestr, uid)) 

            l = []

            for ev in group:
                if ev.type == 'comment':
                    l.append('<b>Comment:</b>\n%s' % ev.comment)
                    pass
                elif ev.type == 'change':
                    l.append('<b>Changed:</b> %s: "%s" -> "%s"' % (ev.field, ev.old, ev.new))
                elif ev.type == 'incrementalchange':
                    l.append('<b>Changed:</b> %s: added: %s , removed: %s' % (ev.field, ev.added, ev.removed))
                elif ev.type == 'reference':
                    l.append('<b>Reference:</b> %s: %s/%s (%s)' % (ev.tracker, ev.ticketnum, ev.comment))
                elif ev.type == 'upload':
                    s = '<b>Upload:</b> %s/%s ' % (issue.absolute_url(), ev.fileid)
                    if ev.comment:
                        s+= ' (%s)' % ev.comment
                    l.append(s)

            definition('\n'.join(l))

            n+=1
        Elements.append(PageBreak())

    IO = cStringIO.StringIO()
    doc = SimpleDocTemplate(IO)
    doc.collector = collector
    doc.collector_title = 'Collector: %s' % collector.title_or_id()
    doc.build(Elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    for f in tempfiles:
        if os.path.exists(f):
            os.unlink(f)

    return IO.getvalue()
