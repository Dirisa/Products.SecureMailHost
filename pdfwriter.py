"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: pdfwriter.py,v 1.19 2003/12/28 18:26:53 ajung Exp $
"""

import os, sys, cStringIO, tempfile
from textwrap import fill
from zLOG import WARNING, LOG
   
try:
    from PIL import Image as PIL_Image
    have_pil = 1
except ImportError: 
    LOG('plonecollectorng', WARNING, 'Python Imaging Library not available. Pdfwriter will not be able to include images in issue PDFs') 
    have_pil = 0

from DateTime import DateTime
from DocumentTemplate.html_quote import html_quote

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

styles = getSampleStyleSheet()

PAGE_HEIGHT = defaultPageSize[1]

def dowrap(text):
    return fill(text, 100)

def break_longlines(text):

    l = []
    for line in text.split('\n'):
        if len(line) > 100:
            l.append(dowrap(line))
        else:
            l.append(line)
    return '\n'.join(l)

def myLaterPages(canvas, doc):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    canvas.setStrokeColorRGB(1,0,0)
    canvas.setLineWidth(5)
    canvas.line(50,45,50,PAGE_HEIGHT-45)
    canvas.line(50,PAGE_HEIGHT-70, 555, PAGE_HEIGHT-70)
    canvas.setFont('Helvetica-Bold',15)
    canvas.drawString(inch, PAGE_HEIGHT-62, doc.collector_title)
    canvas.setFont('Helvetica',11)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.drawString(450, 0.75 * inch, doc.collector.toLocalizedTime(DateTime(), long_format=1))
    canvas.restoreState()

myFirstPage = myLaterPages

Elements = []

HeaderStyle = styles["Heading3"] 
HeaderStyle.fontName = 'Helvetica-Bold'
HeaderStyle.spaceBefore = 3
HeaderStyle.spaceAfter = 1

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.05):
    p = XPreformatted(txt, style)
    Elements.append(p)

ParaStyle = styles["Normal"]
ParaStyle.fontName = 'Helvetica'
ParaStyle.leftIndent = 18

def p(txt):
    return header(txt, style=ParaStyle, sep=0.0)

PreStyle = styles["Code"]

def pre(txt):
    p = Preformatted(txt, PreStyle)
    Elements.append(p)

DefStyle = styles["Definition"]
DefStyle.leftIndent = 18
DefStyle.fontName = 'Helvetica'
DefStyle.spaceBefore = 3
DefStyle.spaceAfter = 1

def definition(txt):
    p = XPreformatted(txt, DefStyle)
    Elements.append(p)


def pdfwriter(collector, ids):

    translate = collector.translate

    tempfiles = []

    for issue_id in ids:
        issue = getattr(collector, str(issue_id))

        header(translate('issue_number', 'Issue #$id', id=issue.title_or_id()))

        header(translate('label_description', 'Description'))
        definition(html_quote(issue.description))

        if issue.solution:
            header(translate('label_solution', 'Solution'))
            definition(html_quote(issue.solution))

        for name in issue.atse_getSchemataNames():
            if name in ('default', 'metadata'): continue
            
            l =[]

            for field in issue.atse_getSchemata(name).fields():
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
                header(translate(name, name.capitalize()))
                definition(dowrap(s))

        for img in issue.objectValues('Portal Image'):

            if have_pil:
                Elements.append(Spacer(100, 0.2*inch))
                fname = tempfile.mktemp() + img.getId()
                tempfiles.append(fname)
                open(fname, 'w').write(str(img.data))
                image = PIL_Image.open(fname)
                width, height= image.size
                ratio = width*1.0 / height
                
                max = 5*inch
                if ratio >  1.0:
                    width = max
                    height = width / ratio
                else:
                    height = max
                    width = height * ratio

                Elements.append(KeepTogether([XPreformatted('Image: %s' % img.title_or_id(), HeaderStyle),
                                              Image(fname, width, height)
                                             ]))

            else:
                p('Image: %s' % img.title_or_id())

            Elements.append(Spacer(100, 0.2*inch))

        header(translate('transcript', 'Transcript'))

        n = 1

        for group in issue.getTranscript().getEventsGrouped(reverse=0):
            datestr = issue.toLocalizedTime(DateTime(group[0].created), long_format=1)
            uid = group[0].user
            header('#%d %s %s (%s)' % (n, translate(issue.lastAction(), issue.lastAction().capitalize()), datestr, uid)) 

            l = []
            comment = None

            for ev in group:
                if ev.type == 'comment':
                    comment = '<b>%s:</b>\n%s' % (translate('comment', 'Comment'), html_quote(ev.comment))
                elif ev.type == 'change':
                    l.append(dowrap('<b>%s:</b> %s: "%s" -> "%s"' % (translate('changed', 'Changed'), ev.field, ev.old, ev.new)))
                elif ev.type == 'incrementalchange':
                    l.append(dowrap('<b>%s:</b> %s: %s: %s , %s: %s' % (translate('changed', 'Changed'), ev.field, translate('added', 'added'), ev.added, translate('removed', 'removed'), ev.removed)))
                elif ev.type == 'reference':
                    l.append(dowrap('<b>%s:</b> %s: %s/%s (%s)' % (translate('reference', 'Reference'), ev.tracker, ev.ticketnum, ev.comment)))
                elif ev.type == 'upload':
                    s = '<b>%s:</b> %s/%s ' % (translate('upload', 'Upload'), issue.absolute_url(), ev.fileid)
                    if ev.comment:
                        s+= ' (%s)' % ev.comment
                    l.append(dowrap(s))

            definition('\n'.join(l))
            if comment: pre(break_longlines(comment))
            n+=1

        Elements.append(PageBreak())

    IO = cStringIO.StringIO()
    doc = SimpleDocTemplate(IO)
    doc.collector = collector
    doc.collector_title = translate('collector_id', 'Collector: $id', id=collector.title_or_id())
    doc.build(Elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    for f in tempfiles:
        if os.path.exists(f):
            os.unlink(f)

    return IO.getvalue()
