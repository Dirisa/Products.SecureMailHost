from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *
from Products.CMFCore import CMFCorePermissions
from schemata import ReferenceManualSectionSchema
from PHCContent import PHCContent
from Products.CMFCore.utils import getToolByName

class HelpCenterReferenceManualSection(PHCContent,OrderedBaseFolder):
    """A section of a reference manual containing ReferenceManualPages and
    other ReferenceManualSections.
    """

    __implements__ = (PHCContent.__implements__,
                      OrderedBaseFolder.__implements__,)

    schema = ReferenceManualSectionSchema
    archetype_name = 'Section'
    meta_type='HelpCenterReferenceManualSection'
    content_icon = 'referencemanual_icon.gif'

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterReferenceManualPage', 
                                'HelpCenterReferenceManualSection')
    allow_discussion = IS_DISCUSSABLE

    typeDescription= 'A Reference Manual Section can contain Reference Manual Pages, and other Reference Manual (Sub-)Sections. Index order is decided by the folder order, use the normal up/down arrow in the folder content view to rearrange content.'
    typeDescMsgId  = 'description_edit_referencemanualsection'

    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/referencemanualsection_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id'          : 'local_roles',
            'name'        : 'Sharing',
            'action'      : 'string:${object_url}/folder_localrole_form',
            'permissions' : (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions

    def getSectionDescription(self):
        """ Returns the description of the section --
        convenience method for ReferenceManualPage
        """
        return self.Description()
    
registerType(HelpCenterReferenceManualSection, PROJECTNAME)

