"""
$Id: PSCImprovementProposalFolder.py,v 1.4 2005/03/12 01:52:01 optilude Exp $
"""

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import registerType
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.content.schemata import PSCImprovementProposalFolderSchema


class PSCImprovementProposalFolder(OrderedBaseFolder):
    """A proposal container has proposals, and a view for the listing."""

    __implements__ = (OrderedBaseFolder.__implements__,)

    content_icon = 'improvementproposal_icon.gif'
    archetype_name = 'Roadmap Section'
    immediate_view = default_view = 'psc_roadmap'
    schema = PSCImprovementProposalFolderSchema

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('PSCImprovementProposal',)

    security = ClassSecurityInfo()

    typeDescMsgId = 'description_edit_improvementproposalcontainer'
    typeDescription = ('A Roadmap Section is used to hold improvement '
                       'proposals. By default you have a single container '
                       'called "improvement", but you can other, more '
                       'specific ones.')

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/psc_roadmap',
            'permissions': (CMFCorePermissions.View,),
        },
        {
        
            'id' : 'edit',
            'name' : 'Edit',
            'action' : 'string:${object_url}/base_edit',
            'permissions' : (CMFCorePermissions.ModifyPortalContent,),
            'visible' : 0,
        },
        {
            'id' : 'metadata',
            'name' : 'Properties',
            'action' : 'string:${object_url}/base_metadata',
            'permissions' : (CMFCorePermissions.ModifyPortalContent,),
            'visible' : 0,
        },
        {
            'id': 'sharing',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,),
        },
    )

    security.declareProtected(CMFCorePermissions.AddPortalContent, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Generate a unique id, by finding the smallest unused number
        among the object in the container.

        This is used when creating objects with createObject.py, to ensure
        that items in this container gets sequentially numbered ids.
        """
        ids = self.objectIds()
        max = 1
        for id in ids:
            try:
                val = int(id)
                if val >= max:
                    max = val + 1
            except ValueError:
                continue
        return str(max)


registerType(PSCImprovementProposalFolder, PROJECTNAME)
