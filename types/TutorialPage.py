from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.PloneHelpCenter.config import *
from schemata import TutorialPageSchema
from PHCContent import PHCContent

class HelpCenterTutorialPage(PHCContent,BaseContent):
    """Part of a tutorial."""

    schema = TutorialPageSchema
    archetype_name = 'Tutorial Page'
    meta_type='HelpCenterTutorialPage'
    content_icon = 'tutorial_icon.gif'

    global_allow = 0
    allow_discussion = 1

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/tutorialpage_view',
                'permissions': (CMFCorePermissions.View,)
                },)


registerType(HelpCenterTutorialPage, PROJECTNAME)
    
