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
Tool that allows for uniform management of ReferenceBags.

$Id: PloneClipboardTool.py,v 1.1 2004/03/24 11:29:58 dpunktnpunkt Exp $
"""

from Products.Archetypes.debug import log, log_exc

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject, SimpleItem
from OFS.ObjectManager import BadRequestException

from interfaces.tool import IPloneClipboardTool
from config import *

class PloneClipboardTool(UniqueObject, SimpleItem):
    __implements__ = IPloneClipboardTool

    security = ClassSecurityInfo()

    def getClipboards(self, create=0):
        mtool = getToolByName(self, 'portal_membership')
        if mtool.isAnonymousUser():
            return None
        
        folder = self._getBagCollection(mtool) # may be acquired
        if not folder:
            if create:
                self.createDefaultClipboards()
                return self.getClipboards()
            else:
                return []
            
        return folder.objectValues()

    def getClipboard(self, id):
        mtool = getToolByName(self, 'portal_membership')
        folder = self._getBagCollection(mtool)
        if hasattr(aq_base(folder), id):
            return getattr(folder, id)
        else:
            return None
    
    def createClipboard(self, id, title=None):
        mtool = getToolByName(self, 'portal_membership')
        wtool = getToolByName(self, 'portal_workflow')

        user = mtool.getAuthenticatedMember()
        home = mtool.getHomeFolder(user.getUserName())
        folder = self._getBagCollection(mtool)
        if not folder:
            self._createBagCollection(home)
            return self.createClipboard(id, title)

        folder.invokeFactory('ReferenceBag', id)
        rb = getattr(folder, id)
        title and rb.setTitle(title)
        wtool.doActionFor(rb, 'hide')

        return rb

    def createDefaultClipboards(self):
        for id in DEFAULT_CLIPBOARD_IDS:
            try:
                self.createClipboard(id)
            except BadRequestException: # assuming "id already in use"
                pass

    def _createBagCollection(self, parent):
        wtool = getToolByName(self, 'portal_workflow')
        ttool = getToolByName(self, 'portal_types')
        
        ttool.constructContent('BagCollection', parent, CLIPBOARDS_FOLDER)
        folder = getattr(parent, CLIPBOARDS_FOLDER)
        folder.setTitle('Clipboards')
        wtool.doActionFor(folder, 'hide')

    def _getBagCollection(self, mtool):
        user = mtool.getAuthenticatedMember()
        home = mtool.getHomeFolder(user.getUserName())
        return getattr(home, CLIPBOARDS_FOLDER, None)


InitializeClass(PloneClipboardTool)

def manage_addPloneClipboardTool(self, id, title, REQUEST=None):
    """Add a PloneClipboardTool."""

    id = str(id)
    title = str(title)
    c = PloneClipboardTool(id, title, None, self)
    self._setObject(id, c)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
