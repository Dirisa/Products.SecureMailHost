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

    content_icon = 'faq_icon.gif'

    schema = FAQSchema
    archetype_name = 'FAQ'
    meta_type = 'HelpCenterFAQ'
    global_allow = 0
    allow_discussion = IS_DISCUSSABLE

    typeDescription= 'A Frequently Asked Question defines a common question with an answer - this is a place to document answers to common questions, not ask them.'
    typeDescMsgId  = 'description_edit_faq'

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
