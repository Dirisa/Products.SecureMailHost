import time, os, tempfile

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4

#precalculate some basics
top_margin = A4[1] - inch
bottom_margin = inch
left_margin = inch
right_margin = A4[0] - inch
frame_width = right_margin - left_margin


def drawPageFrame(canv, issue):

    canv.line(left_margin, top_margin, right_margin, top_margin)
    canv.setFont('Times-Bold',12)
    canv.drawString(left_margin, top_margin + 2, "Collector: %s -  Issue: %s" % (issue.aq_parent.title_or_id(), issue.title_or_id()))
    canv.line(left_margin, top_margin, right_margin, top_margin)

    canv.line(left_margin, bottom_margin, right_margin, bottom_margin)
    canv.drawCentredString(0.5*A4[0], 0.5 * inch,
               "Page %d" % canv.getPageNumber())


def pdfwriter(issue):
    print 1
    fname = tempfile.mktemp()
    print fname
    started = time.time()
    canv = canvas.Canvas(fname)
    canv.setPageCompression(0)
    drawPageFrame(canv, issue)

    #do some title page stuff
    canv.setFont("Times-Bold", 12)
    tx = canv.beginText(left_margin, 10 * inch)
    tx.textLine('Title: %s' % issue.title)
    tx.textLine('Description: %s' % issue.description)
    tx.textLine('Solution: %s' % issue.solution)

    for name in issue.schema_getNames():
        if name in ('default', 'metadata'): continue
        schemata = issue.schema_getSchema(name)

        tx.textLine(name)
        
        for field in schemata.fields():
            tx.textLine('%s: %s' % (field.getName(),field.storage.get(field.getName(), issue)))
        tx.textLine("")
        
    canv.drawText(tx)

    canv.showPage()

    canv.save()

    data = open(fname).read()
    os.unlink(fname)
    return data

