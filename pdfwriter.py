"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: pdfwriter.py,v 1.6 2003/11/15 16:19:10 ajung Exp $
"""

import os, sys, cStringIO, tempfile

try:
    from PIL import Image as PIL_Image
    have_pil = 1
except ImportError: have_pil = 0

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from DateTime import DateTime

styles = getSampleStyleSheet()

PAGE_HEIGHT = defaultPageSize[1]

def myLaterPages(canvas, doc):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Bold',11)
    canvas.drawString(inch, 0.75 * inch, "Page %d " % doc.page)
    canvas.drawString(inch, PAGE_HEIGHT-62, "%s: Issue #%s - %s" % (doc.issue.aq_parent.title_or_id(), doc.issue.getId(), doc.issue.Title()))
    canvas.restoreState()

myFirstPage = myLaterPages


Elements = []

HeaderStyle = styles["Heading2"] 

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.05):
#    para = klass(txt, style)
#    Elements.append(para)

    p = XPreformatted(txt, style)
    Elements.append(p)

ParaStyle = styles["Normal"]

def p(txt):
    return header(txt, style=ParaStyle, sep=0.0)

PreStyle = styles["Code"]

def pre(txt):
    p = Preformatted(txt, PreStyle)
    Elements.append(p)

DefStyle = styles["Definition"]

def definition(txt):
    p = XPreformatted(txt, DefStyle)
    Elements.append(p)


def pdfwriter(issue):

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
            fname = tempfile.mktemp()
            open(fname, 'w').write(fname)
            image = PIL_Image.open(fname)
            width, height= image.size
            ratio = width*1.0 / height

            max = 7*inch
            if ratio > 1.0:
                width = max
                height = max / radio
            else:
                height = max
                width = max / radio

            Elements.append(Image(fname, width, height))
            os.unlink(fname)
        else:
            p('Image: %s' % img.title_or_id())

    header('Transcript')

    groups = issue.getTranscript().getEventsGrouped(reverse=0)
    n = 0
    for group in groups:
        datestr = issue.toPortalTime(DateTime(group[0].created), long_format=1)
        uid = group[0].user
        header('#%d %s %s (%s)' % (len(groups)-n, issue.lastAction().capitalize(), datestr, uid)) 

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

    IO = cStringIO.StringIO()
    doc = SimpleDocTemplate(IO)
    doc.issue = issue
    doc.build(Elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    return IO.getvalue()
