"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: graphviz.py,v 1.7 2004/02/08 15:28:13 ajung Exp $
"""

##########################################################################
# This module creates a graphical representation of the
# issue references using the graph drawing tool Graphviz
# available from www.research.att.com/sw/tools/graphviz
##########################################################################

import os, tempfile
from urllib import unquote

def obj2id(obj):
    """ convert an issue to an ID """
    id = unquote(obj.absolute_url(1))
    id = id.replace('-', '_')
    id = id.replace('/', '_')
    id=  id.replace(' ', '_')
    id=  id.replace('.', '_')
    return id


class Node:
    """ simple node class """

    def __init__(self, issue):
        self.id = obj2id(issue)
        self.url = issue.absolute_url(1)
        self.title = unicode(issue.title_or_id(), issue.getSiteEncoding(), 'ignore').encode('iso-8859-15')
        self.collector_url = issue.aq_parent.absolute_url(1)
        self.collector_id = obj2id(issue.aq_parent)
        self.text = '%s: %s' % (issue.getId(), issue.Title())

    def __str__(self):
        return self.id

    __repr__ = __str__

class Edge:
    """ simple edge class """
    
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __str__(self):
        return '%s -> %s' % (self.src, self.dest)


def build_tree(issue, graphs={}, nodes=[], edges=[]):
    """ build a dependency tree for all references """

    node = Node(issue)
    if not node.id in [n.id for n in nodes]:
        nodes.append(node)
    else:
        return   # stop recursion

    collector_id = obj2id(issue.aq_parent)
    if not collector_id in graphs.keys():
        graphs[collector_id] = {'title': issue.aq_parent.title_or_id(),         
                                'url': issue.aq_parent.absolute_url(1)}

    for ref in (issue.getRefs() or []):
        ref_issue = issue.getPhysicalRoot().restrictedTraverse(unquote(ref.absolute_url(1)))
        e = Edge(node, Node(ref_issue)) 
        if not e in edges: edges.append(e)
        build_tree(ref_issue, graphs, nodes, edges)

    return graphs, nodes, edges


def build_graphviz(graphs, nodes, edges):
    """ Graphviz generation """

    external_edges = []
    fname = tempfile.mktemp()

    fp = open(fname, 'w')
    print >>fp, 'digraph G {'

    for graph in graphs:
        print >>fp, '\tsubgraph cluster_%s {' % graph
        print >>fp, '\t\tlabel="%s";' % graphs[graph]['title']

        printed = []
        for e in edges:
            if e.src.id.startswith(graph) and not e.src.id in printed: 
                print >>fp, '\t\t%s[label="%s"]' % (e.src.id, e.src.title)
                printed.append(e.src.id)
            if e.dest.id.startswith(graph) and not e.dest.id in printed: 
                print >>fp, '\t\t%s[label="%s"]' % (e.dest.id, e.dest.title)
                printed.append(e.dest.id)

        printed = []
        for e in edges:
            if not e.src.id.startswith(graph): continue
            if e.src.id.startswith(graph) and e.dest.id.startswith(graph):
                if  not ( (e.src.id, e.dest.id)) in printed:
                    print >>fp, '\t\t"%s" -> "%s";' % (e.src.id, e.dest.id)
                    printed.append( (e.src.id, e.dest.id) )
            elif e.src.id.startswith(graph):
                    external_edges.append( e )

        print >>fp, '\t}\n'

    for e in external_edges:
        print >>fp, '\t"%s" -> "%s";' % (e.src.text, e.dest.text)

    print >>fp, '}'
    fp.close()
#    print open(fname).read()
    return fname

def viz2image(fname, format='gif', RESPONSE=None):

    outputname = tempfile.mktemp()
    st = os.system('dot -Gpack -T %s  %s > %s' % (format, fname, outputname))
    if st != 0: raise RuntimeError('graphviz execution failed')     
    data = open(outputname).read()

    if format in ('svg',):
        RESPONSE.setHeader('content-type', 'image/svg+xml')
    if format in ('ps',):
        RESPONSE.setHeader('content-type', 'application/postscript')
    else:
        RESPONSE.setHeader('content-type', 'image/%s' % format)
    RESPONSE.write(data)

def viz2map(fname, format='cmap', RESPONSE=None):

    outputname = tempfile.mktemp()
    st = os.system('dot -T %s  %s > %s' % (format, fname, outputname))
    if st != 0: raise RuntimeError('graphviz execution failed')     
    data = open(outputname).read()

    if format in ('svg',):
        RESPONSE.setHeader('content-type', 'image/svg+xml')
    else:
        RESPONSE.setHeader('content-type', 'image/%s' % format)
    RESPONSE.write(data)

