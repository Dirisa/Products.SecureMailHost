from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCFolderSchema as HCSchema
from Products.CMFCore.utils import getToolByName

class PHCFolder:
    """A simple mixin for folderish archetype"""

    typeDescription= 'This is a folder that holds PHC content'
    typeDescMsgId  = 'description_edit_phc'

    content_icon = 'icon.gif'

    schema = HCSchema
    archetype_name = 'PHCFolder'
    meta_type = 'PHCFolder'
    global_allow = 0
    filter_content_types = 1
    
    security = ClassSecurityInfo()

    def getVersionsVocab(self):
        """Get versions vocabulary"""
        return self.aq_base.aq_parent.getVersions_vocab()

    def getSectionsVocab(self):
        """Get sections vocabulary"""
        return self.aq_base.aq_parent.getSections_vocab()
        
    def Versions(self):
        """method to display the versions in a nicer way
        """
        return ", ".join(self.versions)

    def getItems(self, states=[]):	
        """Get items"""
        items = self.contentValues(self.allowed_content_types)

        if states:
            wtool=getToolByName(self, 'portal_workflow', None)
            if wtool:
                getInfoFor=wtool.getInfoFor
                items = [ o for o in items
                          if getInfoFor(o, 'review_state') in states ]
        return items

    def getItemsBySection(self, section, states=[]):	
        """Get items in this section"""
        items = [o for o in self.contentValues(self.allowed_content_types) 
                 if section in o.getSections()]
        if states:
            wtool=getToolByName(self, 'portal_workflow', None)
            if wtool:
                getInfoFor=wtool.getInfoFor
                items = [ o for o in items
                          if getInfoFor(o, 'review_state') in states ]
        return items

    def getSectionsToList(self, states=[]):
        """Sections that have at least one listable item"""
        sections = {}
        max_sections = len(self.sections)

        for o in self.getItems(states):
            for s in o.sections:
                sections[s]=1
            if len(sections) == max_sections:
                break
        return sections.keys()



