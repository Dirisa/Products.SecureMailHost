"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: pdfwriter.py,v 1.24 2004/01/15 12:57:29 ajung Exp $
"""

import os, sys, cStringIO, tempfile
from types import UnicodeType
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
from reportlab import rl_config 
from reportlab.lib.units import inch                              
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

styles = getSampleStyleSheet()

MAX_IMAGE_SIZE = 5*inch
PAGE_HEIGHT = rl_config.defaultPageSize[1]


# Settup custom fonts for UTF8 handling
rl_config.warnOnMissingFontGlyphs = 0
rl_config.TTFSearchPath= list(rl_config.TTFSearchPath) + [ os.path.join(os.path.dirname(__file__), 'ttffonts') ]
pdfmetrics.registerFont(TTFont('NFont', 'rina.ttf'))

#addMapping('NFont', 0, 0, 'NFont')
#addMapping('NFont', 0, 1, 'NFont')
#addMapping('NFont', 1, 0, 'NFont')
#addMapping('NFont', 1, 1, 'NFont')

NORMAL_FONT = 'NFont'

SITE_ENCODING = 'n/a'

def utf8(text):
    if isinstance(text, UnicodeType):
        return text.encode('utf-8')
    else:
        return unicode(text, SITE_ENCODING).encode('utf-8')

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
    canvas.setFont(NORMAL_FONT,15)
    canvas.drawString(inch, PAGE_HEIGHT-62, utf8(doc.collector_title))
    canvas.setFont(NORMAL_FONT,11)
    canvas.drawString(inch, 0.75 * inch, "Page %d" % doc.page)
    canvas.drawString(450, 0.75 * inch, doc.collector.toLocalizedTime(DateTime(), long_format=1))
    canvas.restoreState()

myFirstPage = myLaterPages

Elements = []

HeaderStyle = styles["Heading3"] 
HeaderStyle.fontName = NORMAL_FONT
HeaderStyle.spaceBefore = 3
HeaderStyle.spaceAfter = 1

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.05):
    p = XPreformatted(utf8(txt), style)
    Elements.append(p)

ParaStyle = styles["Normal"]
ParaStyle.fontName = NORMAL_FONT
ParaStyle.leftIndent = 18

def p(txt):
    return header(txt, style=ParaStyle, sep=0.0)

PreStyle = styles["Code"]
PreStyle.fontName = NORMAL_FONT

def pre(txt):
    p = Preformatted(utf8(txt), PreStyle)
    Elements.append(p)

DefStyle = styles["Definition"]
DefStyle.leftIndent = 18
DefStyle.fontName = NORMAL_FONT
DefStyle.spaceBefore = 3
DefStyle.spaceAfter = 1

def definition(txt):
    p = XPreformatted(utf8(txt), DefStyle)
    Elements.append(p)


def pdfwriter(collector, ids):
    global SITE_ENCODING

    SITE_ENCODING = collector.getSiteEncoding()

    translate = collector.translate

    tempfiles = []

    for issue_id in ids:
        issue = getattr(collector, str(issue_id))
        header(translate('issue_number', 'Issue #$id', id='%s: %s' % (issue.getId(), issue.Title())))

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
                
                if ratio >  1.0:
                    width = MAX_IMAGE_SIZE
                    height = width / ratio
                else:
                    height = MAX_IMAGE_SIZE
                    width = height * ratio

                if img.getId() == img.title_or_id():
                    desc = img.getId()
                else:
                    desc = '%s (%s)' % (img.getId(), img.title_or_id())

                Elements.append(KeepTogether([XPreformatted('%s: %s' % (translate('image', 'Image'), desc), HeaderStyle),
                                              Spacer(100, 0.1*inch),
                                              Image(fname, width, height)
                                             ]))

            else:
                p('%s: %s' % (translate('image', 'Image'), img.title_or_id()))

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
                    print repr(ev.comment), type(ev.comment)
                    comment = html_quote(ev.comment)
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
            if comment: 
                definition('<b>%s</b>' % translate('comment', 'Comment'))
                pre(break_longlines(comment))
            n+=1

        # references
        fw_refs = issue.getForwardReferences()
        if fw_refs:
            header(translate('references', 'References'))
            definition('\n'.join(['%s: %s' % (ref.getTargetObject().absolute_url(), ref.comment) for ref in fw_refs ]))

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
