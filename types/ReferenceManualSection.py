sfrom Products.Archetypes.public import *
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

    def getSectionsAndPages(self, states=[]):
        """Get the sections and pages, in order, of this section"""
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
        
    def getParentSectionsAndPages(self, states=[]):
        """Convenience method to get the sections and pages of the parent
        manual or section
        """
        return self.aq_inner.aq_parent.getSectionsAndPages (states)
        
    def getParentItemPosition(self, obj, states=[]):
        """Convenience method to get the position in folder of the parent
        context.
        """
        return self.aq_inner.aq_parent.getItemPosition(obj, states)
    
    
registerType(HelpCenterReferenceManualSection, PROJECTNAME)

