"""
$Id: PSCRelease.py,v 1.3 2005/03/09 18:04:43 dtremea Exp $
"""

import re

from random import random
from DateTime import DateTime

from Acquisition import aq_inner
from Acquisition import aq_parent

from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.utils import folder_modify_fti
from Products.PloneSoftwareCenter.content.schemata import PSCReleaseSchema
from Products.PloneSoftwareCenter.permissions import ADD_CONTENT_PERMISSION

def modify_fti(fti):
    folder_modify_fti(fti, allowed=('PSCFile','PSCFileLink'))


class PSCRelease(OrderedBaseFolder):
    """A Package contains Releases, which have Files."""

    __implements__ = (OrderedBaseFolder.__implements__,)

    archetype_name = 'Software Release'
    immediate_view = default_view = 'psc_release_view'
    content_icon = 'download_icon.gif'
    schema = PSCReleaseSchema

    security = ClassSecurityInfo()

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/psc_release_view',
            'permissions': (CMFCorePermissions.View,),
        },
    )

    typeDescMsgId = 'description_edit_release'
    typeDescription = ('An Release contains details about a planned '
                       'or completed release of the package. Releases '
                       'may be related to specific Improvement Proposals, '
                       'to generate a roadmap. You add the downloadable '
                       'files inside the release.')

# Removed temporarily
#    def initializeArchetype(self, *args, **kw):
#        self.invokeFactory(type_name='PSCDependencyContainer',
#                           id='dependencies')
#        BaseFolder.initializeArchetype(self, *args, **kw)

    security.declareProtected(CMFCorePermissions.View, 'getMaturityVocab')
    def getMaturityVocab(self):
        """Get the available maturity states from the parent package area
        via acqusition.
        """
        return self.getAvailableMaturitiesAsDisplayList()

    security.declareProtected(CMFCorePermissions.View, 'getCompatibilityVocab')
    def getCompatibilityVocab(self):
        """Get the available compatability versions from the parent package area
        via acqusition.
        """
        return self.getAvailableVersionsAsDisplayList()

    security.declareProtected(CMFCorePermissions.View, 'getLicenseVocab')
    def getLicenseVocab(self):
        """Get the available licenses from the parent package area via
         acqusition.
        """
        return self.getAvailableLicensesAsDisplayList()

    #def validateDependency(self, pkg_name, do_raise=1):
    #    pkgs = [d.getPackage() for d in self.dependencies.objectValues()]
    #    if pkg_name in pkgs:
    #        if do_raise:
    #            raise ValueError, ('There is already a dependency '
    #                               'set for this package.')
    #        return 0
    #    return 1

    security.declareProtected(ADD_CONTENT_PERMISSION, 'populateFrom')
    def populateFrom(self, release_id):
        container = aq_parent(aq_inner(self))
        other = container[release_id]
        ids = []
        for obj in other.dependencies.objectValues():
            if not self.validateDependency(obj.getPackage(), 0):
                continue
            ids.append(obj.getId())
        cb = other.dependencies.manage_copyObjects(ids)
        self.dependencies.manage_pasteObjects(cb)

    security.declarePublic('generateTitle')
    def generateTitle(self):
        """Generate the title of the release from the project name +
        the version
        """
        # The first time this is called (it's called like two dozen times
        # when a release is created...) we don't seem to have an acquisition
        # context, so the call to aq_inner fails. Thus, we fall back on a
        # hardcoded string if the parent title lookup fails.
        try:
            version = self.getId()
            parentTitle = self.aq_inner.aq_parent.aq_parent.Title()
        except:
            version = '?'
            parentTitle = '?'
        return "%s %s" % (parentTitle, version)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'validate_id')
    def validate_id(self, value):
        """Validate the id field, ensuring a valid web address was
        entered.
        """
        if not value:
            return "Please provide a version number"
        if re.search (r'[^\w.-]', value):
            return ('Please only use numbers, letters, underscores (_), '
                    'dashes (-) and periods (.) in the version string, no '
                    'other punctuation characters or whitespace')
        else:
            return None

    security.declareProtected(CMFCorePermissions.View,
                              'getRelatedFeaturesVocab')
    def getRelatedFeaturesVocab(self):
        """Get list of PLIPs for this project."""
        items = self.aq_parent.aq_parent.roadmap.objectValues()
        return DisplayList([[i.UID(), i.Title()] for i in items])

    security.declareProtected(ADD_CONTENT_PERMISSION, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """We don't want the behavior of release folder, choosing on
        versions. So use the standard Plone behavior.
        """
        now = DateTime()
        time = '%s.%s' % (now.strftime('%Y-%m-%d'), str(now.millis())[7:])
        rand = str(random())[2:6]
        prefix = ''
        suffix = ''
        if type_name is not None:
            prefix = type_name.replace(' ', '_') + '.'
        prefix = prefix.lower()
        # Generate a fake version number, to signify that the user needs to
        return prefix + time + rand + suffix


registerType(PSCRelease, PROJECTNAME)
