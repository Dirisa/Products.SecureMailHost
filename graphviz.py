"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: graphviz.py,v 1.11 2004/06/29 13:51:45 ajung Exp $
"""

##########################################################################
# This module creates a graphical representation of the
# issue references using the graph drawing tool Graphviz
# available from www.research.att.com/sw/tools/graphviz                                                        
# Also using the pydot module by Ero Carrera
##########################################################################

import os, pydot, tempfile
from urllib import unquote

def build_graph(node, graph, visited):

    def fmt(node):
        print type('%s %s' % (node.getId(), node.Title()))
        s = '%s %s' % (node.getId(), node.Title())
        s = unicode(s, node.getSiteEncoding(), 'ignore').encode('iso-8859-15', 'ignore')
        return s

    if not node.absolute_url(1) in visited:
        visited.append(node.absolute_url(1))

    for ref in node.getForwardReferences(): 
        source = node
        target = ref.getTargetObject()
        e = pydot.Edge(fmt(source), fmt(target), label=ref.comment)
        graph.add_edge(e)
        if not target.absolute_url(1) in visited:
            build_graph(target, graph, visited)


def build_tree2(issue, format):

    G = pydot.Dot()
    build_graph(issue, G, [])
    fname = tempfile.mktemp()
    writer = getattr(G, 'write_%s' % format)
    writer(fname)
    data = open(fname).read()
    os.unlink(fname)
    return data
