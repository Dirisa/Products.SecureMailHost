from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCSchemaWithVersion as HCSchema

class PHCContent:
    """A simple  mixin class to provide contentish functions
    archetype no schema defined"""

    typeDescription= 'Simple PHC content'
    typeDescMsgId  = 'description_edit_phc'

    content_icon = 'icon.gif'

    schema = HCSchema
    archetype_name = 'PHCContent'
    meta_type = 'PHCContent'
    global_allow = 0
    allow_discussion = 1

    security = ClassSecurityInfo()

    def _get_versions_vocab(self):
        return self.aq_parent._get_versions_vocab()
    
    def _get_sections_vocab(self):
        return self.aq_parent._get_sections_vocab()

    def Versions(self):
        """method to display the versions in a nicer way
        """

        # XXX is this really necessary? the widget supports this, doesn't it? ~limi
        result=""
        for version in self.versions:
            if result:
                result=result+", "+ version
            else:
                result=version
        return result

