"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: pdfwriter.py,v 1.4 2003/11/14 19:36:59 ajung Exp $
"""

import os, sys, cStringIO, tempfile

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from DateTime import DateTime

styles = getSampleStyleSheet()

Elements = []

HeaderStyle = styles["Heading2"] 

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.05):
    para = klass(txt, style)
    Elements.append(para)

ParaStyle = styles["Normal"]

def p(txt):
    return header(txt, style=ParaStyle, sep=0.0)

PreStyle = styles["Code"]

def pre(txt):
    s = Spacer(0.05*inch, 0.05*inch)
    Elements.append(s)
    p = Preformatted(txt, PreStyle)
    Elements.append(p)

DefStyle = styles["Definition"]

def definition(txt):
    p = XPreformatted(txt, DefStyle)
    Elements.append(p)


def pdfwriter(issue):

    header('Collector: %s' % issue.aq_parent.title_or_id(), sep=0.1)
    header('Issue: %s' % issue.title_or_id(), sep=0.1)
    header("")

    header("Description")
    definition(issue.description)

    if issue.solution:
        header("Solution")
        definition(issue.solution)

    for name in issue.schema_getNames():
        
        header(name.capitalize())
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
        definition(', '.join(l))

    for img in issue.objectValues('Portal Image'):
        from PIL import Image as PIL_Image
        fname = tempfile.mktemp()
        open(fname, 'w').write(fname)
        image = PIL_Image.open(fname)
        width, height= image.size
        multi = ((height +0.0) / (0.75 * inch))
        width = int(width / multi)
        height = int(height / multi)
        Elements.append(Image(fname, width, height))
        os.unlink(fname)

    header('Transcript')

    groups = issue.getTranscript().getEventsGrouped()
    n = 0
    for group in groups:
        datestr = issue.toPortalTime(DateTime(group[0].created), long_format=1)
        uid = group[0].user
        header('#%d %s %s (%s)' % (len(groups)-n, issue.lastAction().capitalize(), datestr, uid)) 

        l = []

        for ev in group:
            if ev.type == 'comment':
#                l.append('<b>Comment:</b>\n%s' % ev.comment)
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
    doc.build(Elements)

    return IO.getvalue()

