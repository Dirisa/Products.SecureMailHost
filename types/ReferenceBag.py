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

$Id: ReferenceBag.py,v 1.1 2004/03/24 11:30:02 dpunktnpunkt Exp $
"""

from Products.Archetypes.debug import log, log_exc

from Products.ReferenceFolder.types.ReferenceFolder import ReferenceFolder
from Products.ReferenceFolder.config import REFERENCE_NAME
from Products.Archetypes.public import *

from Products.CMFCore.utils import getToolByName


class ReferenceBag(ReferenceFolder):
    portal_type = meta_type = 'ReferenceBag'
    archetype_name = 'Reference Bag'

    # XXX Needs to be moved to ReferenceFolder eventually
    __ac_permissions__ = (
        ('Modify portal content',
         ('manage_cutObjects', 'manage_pasteObjects',
          'manage_renameForm', 'manage_renameObject',
          'manage_renameObjects',)
         ),
        )

    def isCopyBufferPasteable(self):
        if not self.cb_dataValid():
            return 0

        try:
            objects = self.cb_dataItems()
        except KeyError: # item does not exist
            objects = None

        if not objects:
            return 0

        rtool = getToolByName(self, 'reference_catalog')
        for obj in objects:
            if not rtool.isReferenceable(obj):
                return 0

        return len(objects)

    def clear(self):
        self.manage_delObjects(self.objectIds())

def modify_fti(fti):
    fti.update({'allowed_content_types': (),
                'filter_content_types': 1,
                'global_allow': 0})
    
registerType(ReferenceBag)
