from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCFolderSchema as HCSchema
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager

class PHCFolder:
    """A simple mixin for folderish archetype"""

    typeDescription = 'This is a folder that holds PHC content'
    typeDescMsgId = 'description_edit_phc'

    content_icon = 'icon.gif'

    schema = HCSchema
    archetype_name = 'Help Center Folder'
    meta_type = 'PHCFolder'
    global_allow = 0
    filter_content_types = 1

    security = ClassSecurityInfo()

    def getVersionsVocab(self):
        """Get version vocabulary."""
        if hasattr(self,'getVersions_vocab'):
            return self.getVersions_vocab()
        else:
            return list()

    def getSectionsVocab(self):
        """Get sections vocabulary."""
        if hasattr(self,'getSections_vocab'):
            return self.getSections_vocab()
        else:
            return list()

    def Versions(self):
        """Method to display the versions in a nicer way."""
        return ", ".join(getattr(self, 'versions', []))

    def getItems(self, states=[]):
        """Get items."""
        user = getSecurityManager().getUser()
        items = self.contentValues(self.allowed_content_types)
        items = [i for i in items if user.has_permission('View', i)]

        if states:
            wtool=getToolByName(self, 'portal_workflow', None)
            if wtool:
                getInfoFor=wtool.getInfoFor
                items = [o for o in items
                         if getInfoFor(o, 'review_state') in states]
        return items

    def getItemsBySection(self, section, states=[]):
        """Get items in this section"""
        user = getSecurityManager().getUser()
        items = [o for o in self.contentValues(self.allowed_content_types)
                 if section in o.getSections()]
        items = [i for i in items if user.has_permission('View', i) ]
        
        if states:
            wtool=getToolByName(self, 'portal_workflow', None)
            if wtool:
                getInfoFor=wtool.getInfoFor
                items = [o for o in items
                         if getInfoFor(o, 'review_state') in states]
        return items

    def getSectionsToList(self, states=[]):
        """Sections that have at least one listable item"""

        sections = {}
        max_sections = len(self.sections_vocab)

        for o in self.getItems(states):
            for s in o.getSections():
                sections[s]=1
            if len(sections) == max_sections:
                break
        return [s for s in self.getSectionsVocab() if sections.has_key(s)]
