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
PloneClipboard

$Id: __init__.py,v 1.1 2004/03/24 11:29:58 dpunktnpunkt Exp $
"""

from Products.Archetypes.public import *
from config import *
import Products.CMFCore.utils

#Skin
from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory(SKINS_DIR, GLOBALS)

import utils # contains ModuleSecurityInfo
# regsiter validators and make names available at module level:
from Field import ReferenceClipboardWidget, ReferenceClipboardValidator

def initialize(context):
    ##Import Types here to register them
    import types
    
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    Products.CMFCore.utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

