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

$Id: BagCollection.py,v 1.1 2004/03/24 11:30:02 dpunktnpunkt Exp $
"""

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

class BagCollection(OrderedBaseFolder):
    portal_type = meta_type = 'BagCollection'
    archetype_name = 'Collection of Reference Bags'

    actions = (
        {'id':     'view',
         'name':   'view',
         'action': 'string:${object_url}/folder_contents',
         'permissions': (CMFCorePermissions.ListFolderContents,),
         },
        )

def modify_fti(fti):
    fti.update({'allowed_content_types': ('ReferenceBag',),
                'filter_content_types': 1,
                'global_allow': 0})

registerType(BagCollection)
