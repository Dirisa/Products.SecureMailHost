"""
$Id: PloneSoftwareCenter.py,v 1.2 2005/03/09 18:04:43 dtremea Exp $
"""

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions

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

    security.declarePrivate('_getContained')
    def _getContained(self, states, category, portal_type):
        """Get contained objects of type portal_type
        that are in states and have category."""
        my_path = '/'.join(self.getPhysicalPath())
        query = { 'path': my_path,
                  'portal_type':portal_type,
                  'review_state':'published'
                }
        if states:
            query['review_state'] = states
        if category:
            query['categories'] = category
        return self.portal_catalog(query)

    security.declareProtected(CMFCorePermissions.View, 'getPackages')
    def getPackages(self, states=[]):
        """Get catalog brain of packages."""
        return self._getContained(states, None, 'PSCProject')

    security.declareProtected(CMFCorePermissions.View, 'getPackagesByCategory')
    def getPackagesByCategory(self, category, states=[]):
        """Get catalog brains for packages in category."""
        return self._getContained(states, category, 'PSCProject')

    security.declareProtected(CMFCorePermissions.View, 'getReleases')
    def getReleases(self, states=[]):
        """Get catalog brain of releases."""
        return self._getContained(states, None, 'PSCRelease')

    security.declareProtected(CMFCorePermissions.View, 'getReleasesByCategory')
    def getReleasesByCategory(self, category, states=[]):
        """Get catalog brains for releases in category."""
        return self._getContained(states, category, 'PSCRelease')

    security.declareProtected(CMFCorePermissions.View, 'getCategoriesToList')
    def getCategoriesToList(self, states=[]):
        """Categories that have at least one listable package"""
        categories = {}
        avail_categories = self.getAvailableCategories()
        maxCategories = len(avail_categories)
        for o in self.getPackages(states):
            for s in o.getCategories:
                categories[s]=1
            if len(categories) == maxCategories:
                break
        return [s for s in avail_categories if categories.has_key(s)]

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
