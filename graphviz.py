"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: graphviz.py,v 1.15 2004/07/05 19:12:19 ajung Exp $
"""

##########################################################################
# This module creates a graphical representation of the
# issue references using the graph drawing tool Graphviz
# available from www.research.att.com/sw/tools/graphviz                                                        
# Also using the pydot module by Ero Carrera
##########################################################################

import os, pydot, tempfile

MAX_DEPTH = 5

def build_graph(node, graph, visited, depth=0):

    def fmt(node):
        s = '%s %s' % (node.getId(), node.Title())
        s = unicode(s, node.getSiteEncoding(), 'ignore').encode('iso-8859-15', 'ignore')
        return s

    if depth > MAX_DEPTH: return

    if not node.absolute_url(1) in visited:
        visited.append(node.absolute_url(1))

    for ref in node.getForwardReferences(): 
        source = node
        target = ref.getTargetObject()
        c = unicode(ref.comment, node.getSiteEncoding(), 'ignore').encode('iso-8859-15', 'ignore')
        e = pydot.Edge(fmt(source), fmt(target), label=c)
        graph.add_edge(e)
        if not target.absolute_url(1) in visited:
            build_graph(target, graph, visited, depth+1)


def build_tree2(issue, format):

    G = pydot.Dot()
    build_graph(issue, G, [])
    fname = tempfile.mktemp()
    writer = getattr(G, 'write_%s' % format)
    writer(fname)
    data = open(fname).read()
    os.unlink(fname)
    return data
