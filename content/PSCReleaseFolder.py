"""
$Id: PSCReleaseFolder.py,v 1.5 2005/03/11 17:43:31 optilude Exp $
"""

from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import registerType
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.content.schemata import PSCReleaseFolderSchema


class PSCReleaseFolder(OrderedBaseFolder):
    """Folder type for holding releases."""

    __implements__ = (OrderedBaseFolder.__implements__,)

    archetype_name = 'Releases Section'
    immediate_view = default_view = 'psc_releasefolder_view'
    content_icon = 'download_icon.gif'
    schema = PSCReleaseFolderSchema

    security = ClassSecurityInfo()

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('PSCRelease',)

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/psc_releasefolder_view',
            'permissions': (CMFCorePermissions.View,),
        },
        {
            'id': 'sharing',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,),
        }
    )

    typeDescMsgId = 'description_edit_releasefolder'
    typeDescription = ('A Releases Section is used to hold software '
                       'releases. It is given a default short name and '
                       'title to ensure that projects are consistent. '
                       'Please do not rename it.')

    security.declareProtected(CMFCorePermissions.AddPortalContent, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Override for the .py script in portal_scripts with the same name.

        Gives some default names for contained content types.
        """

        # Generate a fake version number, to signify that the user needs to
        # correct it

        # find the highest-used major version
        ids = self.objectIds()

        def getMajor(i):
            try:
                return int(float(i))
            except ValueError:
                return 0

        def getMinor(i):
            if '.' in i:
                try:
                    return int(float(i[i.find('.')+1:]))
                except ValueError:
                    return 0

        majors, minors = ([getMajor(id) for id in ids],
                          [getMinor(id) for id in ids])

        if majors:
            major = max(majors) or 1
        else:
            major = 1

        if minors:
            minor = max(minors)
        else:
            minor = 0

        while '%s.%s' % (major, minor,) in self.objectIds():
            minor += 1
        return '%s.%s' % (major, minor)

    security.declareProtected(CMFCorePermissions.View, 'getUpcomingReleases')
    def getUpcomingReleases(self):
        """Get a list of upcoming releases, in reverse order of effective date.
        """
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(portal_type = 'PSCRelease',
                                    review_state = ['planning', 'in-progress'],
                                    path = '/'.join(self.getPhysicalPath()),
                                    sort_on = 'effective',
                                    sort_order = 'reverse')
        return [r.getObject() for r in res]

    security.declareProtected(CMFCorePermissions.View, 'getPreviousReleases')
    def getPreviousReleases(self):
        """Get a list of previously published releases, in reverse order of
        effective date.
        """
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(portal_type = 'PSCRelease',
                                    review_state = ['published'],
                                    path = '/'.join(self.getPhysicalPath()),
                                    sort_on = 'effective',
                                    sort_order = 'reverse')
        return [r.getObject() for r in res]


registerType(PSCReleaseFolder, PROJECTNAME)
