from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import DefinitionSchema
from PHCContent import PHCContent

class HelpCenterDefinition(PHCContent,BaseContent):
    """A simple archetype"""

    __implements__ = (PHCContent.__implements__,
                      BaseContent.__implements__,)

    content_icon = 'glossary_icon.gif'

    schema = DefinitionSchema
    archetype_name = 'Definition'
    meta_type = 'HelpCenterDefinition'
    global_allow = 0
    allow_discussion = IS_DISCUSSABLE

    typeDescription= 'A Definition defines a special term, and will be listed in the glossary.'
    typeDescMsgId  = 'description_edit_definition'

    actions = (
        {   
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/definition_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions
    

registerType(HelpCenterDefinition, PROJECTNAME)
