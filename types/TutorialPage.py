from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.PloneHelpCenter.config import *
from schemata import TutorialPageSchema
from PHCContent import PHCContent

class HelpCenterTutorialPage(PHCContent,BaseContent):
    """Part of a tutorial."""

    __implements__ = (PHCContent.__implements__,
                      BaseContent.__implements__,)

    schema = TutorialPageSchema
    archetype_name = 'Tutorial Page'
    meta_type='HelpCenterTutorialPage'
    content_icon = 'tutorial_icon.gif'

    global_allow = 0
    allow_discussion = 1

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/tutorialpage_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions


registerType(HelpCenterTutorialPage, PROJECTNAME)
    
