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

$Id: Install.py,v 1.1 2004/03/24 11:30:00 dpunktnpunkt Exp $
"""

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.CMFCore.utils import getToolByName

from Products.PloneClipboard.config import *
from Products.PloneClipboard.PloneClipboardTool \
     import manage_addPloneClipboardTool

from StringIO import StringIO

def install_dependencies(self, out):
    qi = self.portal_quickinstaller
    for dependency in ('Archetypes', 'ReferenceFolder'):
        print >> out, 'Installing dependency %s: ' % dependency,
        qi.installProduct(dependency)
        print >> out, 'done.'

def install_tool(self, out):
    if not hasattr(self, TOOLNAME):
        addTool = manage_addPloneClipboardTool
        addTool(self, TOOLNAME, 'Plone Clipboard Tool')
        print >> out, 'Installed %s.' % TOOLNAME
    else:
        print >> out, '%s already exists.' % TOOLNAME

def add_portlet(self, out):
    myportlet = 'here/portlet_clipboard/macros/portlet'

    left_slots = getattr(self, 'left_slots', ())
    right_slots = getattr(self, 'right_slots', ())

    if myportlet not in left_slots and myportlet not in right_slots:
        self.left_slots = list(left_slots) + [myportlet]
        print >> out, "Added %s to left slots." % myportlet

def install(self):
    out = StringIO()

    install_dependencies(self, out)

    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    install_subskin(self, out, GLOBALS)

    install_tool(self, out)
    add_portlet(self, out)
    
    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()
