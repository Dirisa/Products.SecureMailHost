"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: graphviz.py,v 1.10 2004/06/26 08:37:40 ajung Exp $
"""

##########################################################################
# This module creates a graphical representation of the
# issue references using the graph drawing tool Graphviz
# available from www.research.att.com/sw/tools/graphviz
##########################################################################


import os, pydot, tempfile
from urllib import unquote


def build_graph(node, graph):

    def fmt(node):
        return '%s %s' % (node.getId(), node.Title())

    for ref in node.getForwardReferences(): 
        source = node
        target = ref.getTargetObject()
        e = pydot.Edge(fmt(source), fmt(target), label=ref.comment)
        graph.add_edge(e)


def build_tree2(issue, format):

    G = pydot.Dot()
    build_graph(issue, G)
    fname = tempfile.mktemp()
    writer = getattr(G, 'write_%s' % format)
    writer(fname)
    data = open(fname).read()
    os.unlink(fname)
    return data
