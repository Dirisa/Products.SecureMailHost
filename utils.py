##############################################################################
#
#    Copyright (C) 2004 Material Thought, Inc (dba iTec Solutions)
#    and Contributors <russf@topia.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307,
#
##############################################################################
"""
Utility methods that can be accessed through restricted code.

$Id: utils.py,v 1.1 2004/03/24 11:30:00 dpunktnpunkt Exp $
"""

from Products.Archetypes.debug import log, log_exc
import OFS.CopySupport as CopySupport

from Products.PythonScripts.standard import url_quote_plus
from Products.CMFCore.utils import getToolByName

from AccessControl import ModuleSecurityInfo
modulesec = ModuleSecurityInfo('Products.PloneClipboard.utils')
for fun in ('set_query_values', 'copy_objects_by_path'):
    modulesec.declarePublic(fun)

def set_query_values(url, **overrides):
    # Stolen from create_query_string Plone Pyton Script
    """Creates a query string based on existing query string and overrides."""

    L = []

    if url.find('?') != -1:
        question_mark = url.find('?')
        base = url[:question_mark]
        
        qs = url[question_mark+1:]
        
        entityparts = qs.split('&amp;')
        for entitypart in entityparts:
            ampparts = entitypart.split('&')
            for amppart in ampparts:
                tmp = amppart.split('=',1)
                if len(tmp) > 1:
                    k, v = tmp
                else:
                    k, v = tmp[0], ''

                if k not in overrides:
                    L.append((k, v))
    else:
        base = url

    for k, v in overrides.items():
        L.append((k, url_quote_plus(v)))

    return '%s?%s' % (base, '&amp;'.join(['%s=%s' % (k, v) for k, v in L]))


def copy_objects_by_path(context, paths):
    catalog = getToolByName(context, 'portal_catalog')

    oblist = []

    for path in paths:
        try:
            obj = catalog.searchResults(path=path)[0].getObject()
        except IndexError:
            raise CopySupport.CopyError, \
                  'Invalid path %s' % path
        
        if not obj.cb_isCopyable():
            raise CopySupport.CopyError, \
                  'Copy operation not supported for %s' % obj.getId()

        m = CopySupport.Moniker.Moniker(obj)
        oblist.append(m.dump())

    cp = (0, oblist)
    cp = CopySupport._cb_encode(cp)
    
    resp = context.REQUEST['RESPONSE']
    resp.setCookie('__cp', cp, path=CopySupport.cookie_path(context.REQUEST))
    context.REQUEST['__cp'] = cp
    return cp
