from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCSchema as HCSchema

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

    def getImportanceVocab(self):
        """Get version vocabulary"""
        return IMPORTANCE_VOCAB

    def getVersionsVocab(self):
        """Get version vocabulary"""
        return self.aq_parent.getVersionsVocab()
    
    def getSectionsVocab(self):
        """Get sections vocabulary"""
        return self.aq_parent.getSectionsVocab()

    def Versions(self):
        """method to display the versions in a nicer way
        """

        return ", ".join(getattr(self, 'versions', []))
