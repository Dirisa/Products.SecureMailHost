from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import DefinitionSchema
from PHCContent import PHCContent

class HelpCenterDefinition(PHCContent,BaseContent):
    """A simple archetype"""

    typeDescription= 'You can add a Definition to the Glossary, and it will be reviewed and approved by our documentation team.'
    typeDescMsgId  = 'description_edit_definition'

    content_icon = 'glossary_icon.gif'

    schema = DefinitionSchema
    archetype_name = 'Definition'
    meta_type = 'HelpCenterDefinition'
    global_allow = 0
    allow_discussion = IS_DISCUSSABLE

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/definition_view',
                'permissions': (CMFCorePermissions.View,)
                },)


registerType(HelpCenterDefinition, PROJECTNAME)
