from Products.ATContentTypes.migration.common import *
from Products.ATContentTypes.migration.Walker import CatalogWalker
from Products.ATContentTypes.migration.Migrator import BaseMigrator
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

class Wiki2PHCMigrator(BaseMigrator):
    """
    """
    
    fromType = 'Wiki Page'
    toType   = 'How-to'
    map = {'cook' : 'setBody'}

    def custom(self):
        pass
    
    def renameOld(self):
        """Renames the old object
        
        Unused
        """
        pass

    def createNew(self):
        """Create the new object
        
        use destination from kwargs
        """
        destination = self.kwargs['destination']
        ttool = getToolByName(self.parent, 'portal_types')
        typeInfo = ttool.getTypeInfo(self.toType)
        typeInfo.constructInstance(self.parent, self.new_id)

        self.new = getattr(destinationt, self.new_id)

    def remove(self):
        """Removes the old item
        
        abused to change the workflow state
        """
        wftool = getToolByName(self.parent, 'portal_workflow')
        if wftool.getInfoFor(self.old, 'review_state') in ('published', 'pending'):
            wftool.doActionFor(self.old, 'retract')


def migrate(self):
    catalog = getToolByName(portal, 'portal_catalog')
    destination = self.documentation2.howto
    w = CatalogWalker(Wiki2PHCMigrator, catalog, destination=destination)
    