#------------------------------------------------------------------------------
# Name:         validators.py
# Purpose:      adding TALES validation to Archetypes string and lines fields
#
# Author:       Daniel Nouri <daniel.nouri@con-fuse.org>
#
# Created:      2004-01-28
# RCS-ID:       $Id: validators.py,v 1.4 2004/10/20 20:56:29 dreamcatcher Exp $
# Copyright:    (c) 2004 by Daniel Nouri, Austria
# Licence:      GNU General Public Licence (GPL) Version 2 or later
#------------------------------------------------------------------------------

from Products.validation import validation, interfaces

import Products.CMFCore.Expression as Expression
import Products.PageTemplates.TALES as TALES

from Products.PageTemplates.PageTemplate import PageTemplate

class TALESValidator:
    __implements__ = (interfaces.ivalidator,)

    name = 'talesvalidator'

    def __call__(self, value, *args, **kwargs):
        if type(value) != type([]) and type(value) != type(()):
            value=(value,)
        for expr in value:
            try:
                if expr.strip():
                    Expression.Expression(expr)
            except TALES.CompilerError, e:
                return 'TALES expression "%s" has errors.' % expr
        return 1

validation.register(TALESValidator())

class ZPTValidator:

    __implements__ = (interfaces.ivalidator,)

    name = 'zptvalidator'

    def __call__(self, value, *args, **kwargs):
        pt = PageTemplate()
        pt.write(value)
        errors = pt.pt_errors()
        if errors:
            return ' / '.join(errors)
        return 1

validation.register(ZPTValidator())
