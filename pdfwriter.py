

import os, sys, cStringIO, tempfile

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

PAGE_HEIGHT=defaultPageSize[1]
styles = getSampleStyleSheet()



def myFirstPage(canvas, doc):
    canvas.saveState()
    #canvas.setStrokeColorRGB(1,0,0)
    #canvas.setLineWidth(5)
    #canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Bold',16)
    canvas.drawString(108, PAGE_HEIGHT-108, Title)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
    canvas.restoreState()

def myLaterPages(canvas, doc):
    #canvas.drawImage("snkanim.gif", 36, 36)
    canvas.saveState()
    #canvas.setStrokeColorRGB(1,0,0)
    #canvas.setLineWidth(5)
    #canvas.line(66,72,66,PAGE_HEIGHT-72)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
    canvas.restoreState()

Elements = []

HeaderStyle = styles["Heading1"] # XXXX

def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.1):
    s = Spacer(0.1*inch, sep*inch)
    Elements.append(s)
    para = klass(txt, style)
    Elements.append(para)

ParaStyle = styles["Normal"]

def p(txt):
    return header(txt, style=ParaStyle, sep=0.0)

PreStyle = styles["Code"]

def pre(txt):
    s = Spacer(0.1*inch, 0.1*inch)
    Elements.append(s)
    p = Preformatted(txt, PreStyle)
    Elements.append(p)


def pdfwriter(issue):

    header('Collector: %s' % issue.aq_parent.title_or_id(), sep=0.1)
    header('Issue: %s' % issue.title_or_id(), sep=0.1)
  

    header("")

    header("Description")
    pre(issue.description)

    if issue.solution:
        header("Solution")
        pre(issue.solution)

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
        p(', '.join(l))

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


    IO = cStringIO.StringIO()
    doc = SimpleDocTemplate(IO)
    doc.build(Elements)

    return IO.getvalue()

