#
# The PSCProject Package Area container
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box.
#

from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.public import OrderedBaseFolder
from Products.Archetypes.public import registerType

from Products.PloneSoftwareCenter.config import *
from Products.PloneSoftwareCenter.factory import factoryRegistry
from Products.PloneSoftwareCenter.factory import getFactory
from Products.PloneSoftwareCenter.utils import folder_modify_fti
from AccessControl import getSecurityManager

from schemata import PloneSoftwareCenterSchema
            
class PloneSoftwareCenter(OrderedBaseFolder):
    """A simple folderish archetype"""

    __implements__ = (OrderedBaseFolder.__implements__,)

    content_icon = 'product_icon.gif'

    archetype_name = 'Software Center'
    metatype = 'PloneSoftwareCenter'
    immediate_view = default_view = 'plonesoftwarecenter_view'
    global_allow = 1
    filter_content_types = 1
    allowed_content_types = ('PSCProject', )
    schema = PloneSoftwareCenterSchema
       
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/plonesoftwarecenter_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )

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

    def getPackages(self, states=[]):
        """Get catalog brain of packages."""

        return self._getContained(states, None, 'PSCProject')

    def getPackagesByCategory(self, category, states=[]):
        """Get catalog brains for packages in category."""

        return self._getContained(states, category, 'PSCProject')

    def getReleases(self, states=[]):
        """Get catalog brain of releases."""

        return self._getContained(states, None, 'PSCRelease')

    def getReleasesByCategory(self, category, states=[]):
        """Get catalog brains for releases in category."""

        return self._getContained(states, category, 'PSCRelease')

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

    def getAvailableLicensesAsDisplayList(self):
        """Get licenses in DisplayList form."""

        return self.getField('availableLicenses').getAsDisplayList(self)

    def getAvailableMaturitiesAsDisplayList(self):
        """Get licenses in DisplayList form."""

        return self.getField('availableMaturities').getAsDisplayList(self)

    def getAvailableVersionsAsDisplayList(self):
        return DisplayList ([(item, item) for item in self.getAvailableVersions ()])

registerType(PloneSoftwareCenter, PROJECTNAME)
