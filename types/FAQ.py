from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import FAQSchema

class HelpCenterFAQ(BaseContent):
    """A simple archetype"""

    typeDescription= 'You can add a Frequently Asked Question (preferrably with an answer), and it will be reviewed and approved by our documentation team.'
    typeDescMsgId  = 'description_edit_faq'

    content_icon = 'faq_icon.gif'

    schema = FAQSchema
    archetype_name = 'FAQ'
    meta_type = 'HelpCenterFAQ'
    global_allow = 0
    allow_discussion = 1

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/faq_view',
                'permissions': (CMFCorePermissions.View,)
                },)

    security = ClassSecurityInfo()

    def _get_versions_vocab(self):
        return self.aq_parent._get_versions_vocab()
    
    def _get_sections_vocab(self):
        return self.aq_parent._get_sections_vocab()

    
registerType(HelpCenterFAQ, PROJECTNAME)
