from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *
from Products.CMFCore import CMFCorePermissions
from schemata import ReferenceManualSchema
from PHCContent import PHCContent
from Products.CMFCore.utils import getToolByName

class HelpCenterReferenceManual(PHCContent,OrderedBaseFolder):
    """A reference manual containing ReferenceManualPages,
    ReferenceManualSections, Files and Images.
    """

    __implements__ = (PHCContent.__implements__,
                      OrderedBaseFolder.__implements__,)

    schema = ReferenceManualSchema
    archetype_name = 'Reference Manual'
    meta_type='HelpCenterReferenceManual'
    content_icon = 'referencemanual_icon.gif'

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterReferenceManualPage', 
                            'HelpCenterReferenceManualSection', 'Image', 'File')
    allow_discussion = IS_DISCUSSABLE

    typeDescription= 'A Reference Manual can contain Reference Manual Pages and Sections, Images and Files. Index order is decided by the folder order, use the normal up/down arrow in the folder content view to rearrange content.'
    typeDescMsgId  = 'description_edit_referencemanual'

    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/referencemanual_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id'          : 'local_roles',
            'name'        : 'Sharing',
            'action'      : 'string:${object_url}/folder_localrole_form',
            'permissions' : (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions

    def getReferenceManualDescription(self):
        """ Returns the description of the ReferenceManual -- 
        convenience method for ReferenceManualPage
        """
        return self.Description()

    def getSectionsAndPages(self, states=[]):
        """Get the sections and pages, in order, of this manual"""
        items = self.contentValues(('HelpCenterReferenceManualSection',
                                    'HelpCenterReferenceManualPage',))

        if states:
            wtool=getToolByName(self, 'portal_workflow', None)
            if wtool:
                getInfoFor=wtool.getInfoFor
                items = [ o for o in items
                          if getInfoFor(o, 'review_state') in states ]
        return items

    def getItemPosition(self, obj, states=[]):
        """Get position in folder of the current context"""

        items = self.getSectionsAndPages(states)
        return items.index(obj)

registerType(HelpCenterReferenceManual, PROJECTNAME)

