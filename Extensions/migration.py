from Products.ATContentTypes.migration.common import *
from Products.ATContentTypes.migration.Walker import CatalogWalker
from Products.ATContentTypes.migration.Migrator import BaseMigrator
from Products.ATContentTypes.migration.Migrator import CMFItemMigrator
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

BASE_PATH = '/testsite/documentation/howto'

class DocumentationWalker(CatalogWalker):
    """Overwrite walk to start from a base path
    """
    
    def walk(self, **kwargs):
        """Walks around and returns all objects which needs migration

        :return: objects (with acquisition wrapper) that needs migration
        :rtype: generator
        """
        LOG("fromType: " + str(self.fromType))
        catalog = self.catalog

        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            # usage of Language is required for LinguaPlone
            brains = catalog(portal_type = self.fromType,
                             Language = catalog.uniqueValuesFor('Language'),
                             path = BASE_PATH,
                            )
        else:
            brains = catalog(portal_type = self.fromType,
                             path = BASE_PATH,)

        for brain in brains:
            obj = brain.getObject()
            if obj:
                yield obj
                # XXX safe my butt
                obj._p_deactivate()

class Wiki2PHCMigrator(CMFItemMigrator):
#class Wiki2PHCMigrator(BaseMigrator):
    """
    """
    
    fromType = 'Wiki Page'
    toType   = 'HelpCenterHowTo'
    #map = {'render' : 'setBody'}
    
    def __init__(self, obj, **kwargs):
        BaseMigrator.__init__(self, obj, **kwargs)
        self.new_id = mkNiceId(self.new_id)

    def custom(self):
        print '%s -> %s' % (self.old.absolute_url(1), self.new.absolute_url(1))
        data = self.old.read()
        self.new.setBody(data, encoding='utf-8', mimetype='text/structured')
        self.new.setRelated_keywords((self.orig_id,))
    
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
        typeInfo.constructInstance(destination, self.new_id)
        self.new = getattr(destination, self.new_id)

    def remove(self):
        """Removes the old item
        
        abused to change the workflow state
        """
        wftool = getToolByName(self.parent, 'portal_workflow')
        wftool.doActionFor(self.new, 'submit')
        #if wftool.getInfoFor(self.old, 'review_state') in ('published', 'pending'):
        #    wftool.doActionFor(self.old, 'retract')


def mkNiceId(id):
    """
    """
    assert(isinstance(id, str))
    newId = []
    for s in id:
        if s.isupper():
            newId.append('-'+s.lower())
        else:
            newId.append(s)
    strid = ''.join(newId)
    if strid.startswith('-'):
        strid = strid[1:]
    return strid

def migrate(self):
    catalog = getToolByName(self, 'portal_catalog')
    destination = self.documentation.howto2.howto
    #w = CatalogWalker(Wiki2PHCMigrator, catalog, destination=destination)
    w = DocumentationWalker(Wiki2PHCMigrator, catalog)
    return w.go( destination=destination)
