from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCSchema as HCSchema

# Get HistoryAwareMixin on all our types:

# This is currently in ATContentTypes, which introduces a dependency we'd rather 
# do without. It's slated to move to Archetypes itself, so try that first in the
# hope that it's there. If both fail, fall back on a dummy HistoryAwareMixin
# which will let us continue as normal. Yep, it's another optilude hack (tm).

try:
    from Products.Archetypes.HistoryAware import HistoryAwareMixin
except ImportError:
    try:
        from Products.ATContentTypes.HistoryAware import HistoryAwareMixin
    except ImportError:
        
        class HistoryAwareMixin:
            """Dummy class when we can't find the real McCoy"""
            
            __implements__ = ()
            actions        = ()

class PHCContent (HistoryAwareMixin):
    """A simple  mixin class to provide contentish functions
    archetype no schema defined"""

    #typeDescription= 'Simple PHC content'
    #typeDescMsgId  = 'description_edit_phc'

    #content_icon = 'icon.gif'

    #schema = HCSchema
    #archetype_name = 'PHCContent'
    #meta_type = 'PHCContent'
    #global_allow = 0
    #allow_discussion = 1

    security = ClassSecurityInfo()
    
    __implements__ = (HistoryAwareMixin.__implements__,)
    actions = () + HistoryAwareMixin.actions

    security.declareProtected (CMFCorePermissions.View, 'getImportanceVocab')
    def getImportanceVocab(self):
        """Get importance vocabulary"""
        return self.aq_parent.getImportanceVocab ()

    security.declareProtected (CMFCorePermissions.View, 'getVersionsVocab')
    def getVersionsVocab(self):
        """Get version vocabulary"""
        return self.aq_parent.getVersionsVocab()
    
    security.declareProtected (CMFCorePermissions.View, 'getSectionsVocab')
    def getSectionsVocab(self):
        """Get sections vocabulary"""
        return self.aq_parent.getSectionsVocab()

    security.declareProtected (CMFCorePermissions.View, 'Versions')
    def Versions(self):
        """method to display the versions in a nicer way
        """

        return ", ".join(getattr(self, 'versions', []))
    
    security.declareProtected (CMFCorePermissions.View, 'isOutdated')
    def isOutdated(self):
        """Check the current versions of the PHC root container against the
        versions of this item. If the version of this item is not in the list
        of current versions, return 1, else return 0
        """
        
        myVersions = getattr(self, 'versions', [])
        
        # Acquire current versions
        currentVersions = self.getCurrentVersions ()
        
        for v in myVersions:
            if v in currentVersions:
                # Not outdated - we match one of the current versions
                return 0
                
        # Outdated - we didn't match anything
        return 1
        
    security.declareProtected (CMFCorePermissions.View, 'getReferencedItems') 
    def getReferencedItems(self):
        """method to fetch the referenced items in context of
           config and permissions
        """
        if ENABLE_REFERENCES:
            objs = [o for o in self.getReferenced_items() if self.portal_membership.checkPermission('View', o)]
            return objs
        else:
            return None
