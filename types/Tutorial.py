from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *
from Products.CMFCore import CMFCorePermissions
from schemata import TutorialSchema
from PHCContent import PHCContent
from Products.CMFCore.utils import getToolByName

class HelpCenterTutorial(PHCContent,OrderedBaseFolder):
    """A tutorial containing TutorialPages, Files and Images."""

    __implements__ = (PHCContent.__implements__,
                      OrderedBaseFolder.__implements__,)

    schema = TutorialSchema
    archetype_name = 'Tutorial'
    meta_type='HelpCenterTutorial'
    content_icon = 'tutorial_icon.gif'

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorialPage', 'Image', 'File')
    allow_discussion = IS_DISCUSSABLE

    typeDescription= 'A Tutorial can contain Tutorial Pages, Images and Files. Index order is decided by the folder order, use the normal up/down arrow in the folder content view to rearrange content.'
    typeDescMsgId  = 'description_edit_tutorial'

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/tutorial_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions

    def getTutorialDescription(self):
        """ Returns the description of the Tutorial--convenience method for TutorialPage """
        return self.Description()


    def getPages(self, states=[]):
        """Get items"""
        items = self.contentValues('HelpCenterTutorialPage')

        if states:
            wtool=getToolByName(self, 'portal_workflow', None)
            if wtool:
                getInfoFor=wtool.getInfoFor
                items = [ o for o in items
                          if getInfoFor(o, 'review_state') in states ]
        return items

    def getPagePosition(self, obj, states=[]):
        """Get position in folder of the current context"""

        items = self.getPages(states)
        return items.index(obj)

registerType(HelpCenterTutorial, PROJECTNAME)

