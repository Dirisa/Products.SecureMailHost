from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import FAQSchema
from PHCContent import PHCContent

class HelpCenterFAQ(PHCContent,BaseContent):
    """A simple archetype"""

    __implements__ = (PHCContent.__implements__,
                      BaseContent.__implements__,)

    typeDescription= 'You can add a Frequently Asked Question (with an answer - this is not a place to ask questions), and it will be reviewed and approved by our documentation team.'
    typeDescMsgId  = 'description_edit_faq'

    content_icon = 'faq_icon.gif'

    schema = FAQSchema
    archetype_name = 'FAQ'
    meta_type = 'HelpCenterFAQ'
    global_allow = 0
    allow_discussion = IS_DISCUSSABLE

    actions = (
        {'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/faq_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions


registerType(HelpCenterFAQ, PROJECTNAME)
