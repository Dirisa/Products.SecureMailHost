"""
$Id: PloneSoftwareCenter.py,v 1.6 2005/03/12 04:00:41 optilude Exp $
"""

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import registerType
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.content.schemata import PloneSoftwareCenterSchema


class PloneSoftwareCenter(OrderedBaseFolder):
    """A simple folderish archetype for the Software Center."""

    __implements__ = (OrderedBaseFolder.__implements__,)

    content_icon = 'product_icon.gif'

    archetype_name = 'Software Center'
    metatype = 'PloneSoftwareCenter'
    immediate_view = default_view = 'plonesoftwarecenter_view'

    global_allow = 1
    filter_content_types = 1
    allowed_content_types = ('PSCProject',)
    schema = PloneSoftwareCenterSchema

    security = ClassSecurityInfo()

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/plonesoftwarecenter_view',
            'permissions': (CMFCorePermissions.View,),
        },
    )

    security.declarePrivate('validate_availableCategories')
    def validate_availableCategories(self, value):
        """Ensure that when setting available categories, we don't accidentally
        set the same category id as an existing project.
        """
        catalog = getToolByName(self, 'portal_catalog')
        projects = catalog.searchResults(
                            portal_type = 'PSCProject',
                            path = '/'.join(self.getPhysicalPath()))
        
        categoryIds = [v.split('|')[0] for v in value]
        projectIds = [p.getId for p in projects]

        empty = []
        invalid = []
        for cat in categoryIds:
            if not cat:
                empty.append(cat)
            elif cat in projectIds or categoryIds.count(cat) > 1:
                invalid.append(cat)
    
        if empty:
            return "Please enter categories as short-name|Long name."
        if invalid:
            return "The following short category names are in use, either " \
                   "by another category, or by a project in the software " \
                   "center: %s." % (','.join(invalid))
        else:
            return None
            
    security.declarePrivate('_getContained')
    def _getContained(self, states, category, portal_type, limit=None, 
                        sort_on='effective', sort_order='reverse'):
        """Get contained objects of type portal_type
        that are in states and have category."""
        
        catalog = getToolByName(self, 'portal_catalog')
        my_path = '/'.join(self.getPhysicalPath())
        query = { 'path'         : my_path,
                  'portal_type'  : portal_type,
                  'review_state' : 'published',
                }
                
        if states:
            query['review_state'] = states
        if category:
            query['getCategories'] = category
        if limit:
            query['sort_limit'] = limit
        if sort_on:
            query['sort_on'] = sort_on
        if sort_order:
            query['sort_order'] = sort_order
            
        results = catalog.searchResults(query)
        
        if limit:
            return results[:int(limit)]
        else:
            return results

    security.declareProtected(CMFCorePermissions.View, 'getPackages')
    def getPackages(self, states=[], limit=None):
        """Get catalog brain of packages."""
        return self._getContained(states, None, 'PSCProject', limit)

    security.declareProtected(CMFCorePermissions.View, 'getPackagesByCategory')
    def getPackagesByCategory(self, category, states=[], limit=None):
        """Get catalog brains for packages in category."""
        return self._getContained(states, category, 'PSCProject', limit,
                                    sort_on='sort_title')

    security.declareProtected(CMFCorePermissions.View, 'getReleases')
    def getReleases(self, states=[], limit=None):
        """Get catalog brain of releases."""
        return self._getContained(states, None, 'PSCRelease', limit)

    security.declareProtected(CMFCorePermissions.View, 'getReleasesByCategory')
    def getReleasesByCategory(self, category, states=[], limit=None):
        """Get catalog brains for releases in category."""
        return self._getContained(states, category, 'PSCRelease', limit)

    security.declareProtected(CMFCorePermissions.View, 'getCategoriesToList')
    def getCategoriesToList(self, states=[]):
        """Categories that have at least one listable package"""
        vocab = self.getAvailableCategoriesAsDisplayList()
        catalog = getToolByName(self, 'portal_catalog')
        uniqueCategories = catalog.uniqueValuesFor('getCategories')
        
        categories = DisplayList()
        for cat in uniqueCategories:
            value = vocab.getValue(cat)
            # Ensure the value came from our vocab and not some other 
            # getCategories somewhere
            if value:
                categories.add(cat, value)
                
        return categories.sortedByValue()

    security.declareProtected(CMFCorePermissions.View, 'getCategoryName')
    def getCategoryName(self, category):
        """Get the long name of a category.
        """
        return self.getAvailableCategoriesAsDisplayList().getValue(category)

    security.declareProtected(CMFCorePermissions.View,
                              'getAvailableCategoriesAsDisplayList')
    def getAvailableCategoriesAsDisplayList(self):
        """Get categories in DisplayList form."""
        return self.getField('availableCategories').getAsDisplayList(self)

    security.declareProtected(CMFCorePermissions.View,
                              'getAvailableLicensesAsDisplayList')
    def getAvailableLicensesAsDisplayList(self):
        """Get licenses in DisplayList form."""
        return self.getField('availableLicenses').getAsDisplayList(self)

    security.declareProtected(CMFCorePermissions.View,
                              'getAvailableMaturitiesAsDisplayList')
    def getAvailableMaturitiesAsDisplayList(self):
        """Get licenses in DisplayList form."""
        return self.getField('availableMaturities').getAsDisplayList(self)

    security.declareProtected(CMFCorePermissions.View,
                              'getAvailableVersionsAsDisplayList')
    def getAvailableVersionsAsDisplayList(self):
        return DisplayList([(item, item) for item in self.getAvailableVersions()])


registerType(PloneSoftwareCenter, PROJECTNAME)
