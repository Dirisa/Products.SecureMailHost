"""
$Id: PSCImprovementProposalFolder.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject
from Products.Archetypes.public import OrderedBaseFolder, registerType

from Products.PloneSoftwareCenter.config import *
from Products.PloneSoftwareCenter.utils import folder_modify_fti

from schemata import PSCImprovementProposalFolderSchema
from Products.CMFCore import CMFCorePermissions

def modify_fti(fti):
    folder_modify_fti(fti, allowed=('PSCImprovementProposal',))

    #Set view action to improvementproposal_listing
    for a in fti['actions']:
        if a['id'] == 'view':
            a['action'] = 'string:${object_url}/psc_roadmap'
            break

class PSCImprovementProposalFolder(OrderedBaseFolder, UniqueObject):
    """ A proposal container has proposals, and a view for the listing. """

    content_icon = 'improvementproposal_icon.gif'
    archetype_name = 'Roadmap Section'
    immediate_view = default_view = 'psc_roadmap'
    
    actions =({
        'id'          : 'sharing',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,)
        },
        )

    schema = PSCImprovementProposalFolderSchema

    typeDescription= "A Roadmap Section is used to hold improvement proposals. By default you have a single container called 'improvement', but you can other, more specific ones."
    typeDescMsgId  = 'description_edit_improvementproposalcontainer'

    security = ClassSecurityInfo()

    security.declareProtected (ADD_CONTENT_PERMISSION, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Generate a unique id, by finding the smallest unused number 
        among the object in the container. This is used when creating
        objects with createObject.py, to ensure that items in this container
        gets sequentially numbered ids.
        """
                        
        ids = self.objectIds ()
        max = 1
        
        for id in ids:
            try:
                val = int (id)
                if val >= max:
                    max = val + 1
            except ValueError:
                continue
                
        return str (max)


registerType(PSCImprovementProposalFolder, PROJECTNAME)

