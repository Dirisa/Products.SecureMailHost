"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: references.py,v 1.1 2003/09/30 08:32:34 ajung Exp $
"""

##########################################################################
# This module creates a graphical representation of the
# issue references using the graph drawing tool Graphviz
# available from www.research.att.com/sw/tools/graphviz
##########################################################################

import os, tempfile
from urllib import unquote

def issue2id(issue):
    """ convert an issue to an ID """
    url = unquote(issue.absolute_url(1))
    url = url.replace('/', '_')
    url = url.replace(' ', '_')
    return url

def collector2id(collector):
    """ convert an collector to an ID """
    url = unquote(collector.absolute_url(1))
    url = url.replace('/', '_')
    url = url.replace(' ', '_')
    return url


class Node:
    """ simple node class """

    def __init__(self, issue):
        self.id = issue2id(issue)
        self.url = issue.absolute_url(1)
        self.collector_url = issue.aq_parent.absolute_url(1)

class Edge:
    """ simple edge class """
    
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __cmp__(self, o):
        return self.src==o.src and self.dest==o.dest


def build_tree(issue, graphs={}, nodes=[], edges=[]):
    """ build a dependency tree for all references """

    node = Node(issue)
    if not node.id in [n.id for n in nodes]:
        nodes.append(node)
    else:
        return   # stop recursion

    collector_id = collector2id(issue.aq_parent)
    if not graphs.has_key(collector_id):
        graphs[collector_id] = []

    if not node.id in graphs[collector_id]:
        graphs[collector_id].append(node)
    
    for ref in issue.getReferences():
        ref_issue = issue.unrestrictedTraverse(ref.getURL())
        e = Edge(node, Node(ref_issue)) 
        edges.append(e) 
        build_tree(ref_issue, graphs, nodes, edges)

    return graphs, nodes, edges


def build_graphviz(graphs, nodes, edges):
    """ Graphviz generation """
 
    external_edges = []

    fname = tempfile.mktemp()
    fp = open(fname, 'w')
    print >>fp, 'digraph G {'
    for graph in graphs.keys():
        print >>fp, '\tsubgraph %s {' % graph
        print >>fp, '\t\tlabel = "%s";' % graph

        for e in edges:
            if e.src.id.startswith(graph) and e.dest.id.startswith(graph):
                print >>fp, '\t\t%s -> %s' % (e.src.id, e.dest.id)
            else:
                if not e in external_edges and e.src.id.startswith(graph):
                    external_edges.append( e )

        print >>fp, '\t}'

    for e in external_edges:
        print >>fp, '\t%s -> %s' % (e.src.id, e.dest.id)

    print >>fp, '}'
    fp.close()

#    print open(fname).read()
    imgname = tempfile.mktemp()
    os.system('/opt/graphviz/bin/dot -T gif %s > %s' % (fname, imgname))
    os.unlink(fname)

    return imgname
    
