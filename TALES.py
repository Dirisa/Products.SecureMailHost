#------------------------------------------------------------------------------
# Name:         TALES.py
# Purpose:      adding TALES support to string and lines fields
#
# Author:       Daniel Nouri <daniel.nouri@con-fuse.org>
#
# Created:      2004-01-28
# RCS-ID:       $Id: TALES.py,v 1.1 2004/05/22 15:50:58 yenzenz Exp $
# Copyright:    (c) 2004 by Daniel Nouri, Austria
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
import Products.CMFCore.Expression as Expression

try:
    from Products.CMFCore.Expression import getExprContext
except ImportError:
    def getExprContext(context, object=None):
        request = getattr(context, 'REQUEST', None)
        if request:
            cache = request.get('_ec_cache', None)
            if cache is None:
                request['_ec_cache'] = cache = {}
            ec = cache.get( id(object), None )
        else:
            ec = None

        if ec is None:
            utool = getToolByName(context, 'portal_url')
            portal = utool.getPortalObject()
            if object is None or not hasattr(object, 'aq_base'):
                folder = portal
            else:
                folder = object
                # Search up the containment hierarchy until we find an
                # object that claims it's a folder.
                while folder is not None:
                    if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
                        # found it.
                        break
                    else:
                        folder = aq_parent(aq_inner(folder))
            ec = Expression.createExprContext(folder, portal, object)
        if request:
            cache[ id(object) ] = ec
        return ec


class TALESLines:
    def compileExpressions(self, name):
        lines = self.getField(name).get(self)
        if not lines: return

        expressions = getattr(self, '_v_expressions', {})
        li = []
        expressions[name] = li

        for line in lines:
            li.append(Expression.Expression(line))
        
        self._v_expressions = expressions
        
    def getEvaluatedExpressions(self, name):
        if not getattr(self.aq_base, '_v_expressions', {}).has_key(name):
            self.compileExpressions(name)

        r = []
        
        for expr in self._v_expressions.get(name, []):
            r.append(str(expr(getExprContext(self, self))))
        return r

class TALESString:
    def compileExpression(self, name):
        value = self.getField(name).get(self)
        if not value: return

        expressions = getattr(self, '_v_expressions', {})
        expressions[name] = Expression.Expression(value)

        self._v_expressions = expressions

    def getEvaluatedExpression(self, name):
        if not getattr(self.aq_base, '_v_expressions', {}).has_key(name):
            self.compileExpression(name)

        expr = self._v_expressions.get(name, None)
        if not expr:
            return None
        
        return str(expr(getExprContext(self, self)))
