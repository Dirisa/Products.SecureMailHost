"""
$Id: PSCImprovementProposalFolder.py,v 1.3 2005/03/11 17:43:31 optilude Exp $
"""

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import registerType
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.utils import folder_modify_fti
from Products.PloneSoftwareCenter.content.schemata import PSCImprovementProposalFolderSchema

def modify_fti(fti):
    folder_modify_fti(fti, allowed=('PSCImprovementProposal',))

    #Set view action to improvementproposal_listing
    for a in fti['actions']:
        if a['id'] == 'view':
            a['action'] = 'string:${object_url}/psc_roadmap'
            break


class PSCImprovementProposalFolder(OrderedBaseFolder):
    """A proposal container has proposals, and a view for the listing."""

    __implements__ = (OrderedBaseFolder.__implements__,)

    content_icon = 'improvementproposal_icon.gif'
    archetype_name = 'Roadmap Section'
    immediate_view = default_view = 'psc_roadmap'
    schema = PSCImprovementProposalFolderSchema

    security = ClassSecurityInfo()

    typeDescMsgId = 'description_edit_improvementproposalcontainer'
    typeDescription = ('A Roadmap Section is used to hold improvement '
                       'proposals. By default you have a single container '
                       'called "improvement", but you can other, more '
                       'specific ones.')

    actions = (
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
