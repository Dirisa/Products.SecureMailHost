from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import LinkSchema
from PHCContent import PHCContent

class HelpCenterLink(PHCContent,BaseContent):
    """A simple archetype"""

    __implements__ = (PHCContent.__implements__,
                      BaseContent.__implements__,)


    typeDescription= 'Help Center links are links to other documentation, etc.'
    typeDescMsgId  = 'description_edit_link'

    content_icon = 'helplink_icon.gif'

    schema = LinkSchema
    archetype_name = 'Link'
    meta_type = 'HelpCenterLink'
    global_allow = 0
    allow_discussion = IS_DISCUSSABLE

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/helplink_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions


registerType(HelpCenterLink, PROJECTNAME)
