"""
$Id: PSCProject.py,v 1.16 2005/03/12 04:00:41 optilude Exp $
"""

from AccessControl import ClassSecurityInfo

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import registerType
from Products.Archetypes.public import OrderedBaseFolder

from Products.PloneSoftwareCenter import config
from Products.PloneSoftwareCenter.factory import getFactory
from Products.PloneSoftwareCenter.factory import factoryRegistry
from Products.PloneSoftwareCenter.utils import folder_modify_fti
from Products.PloneSoftwareCenter.content.schemata import PSCProjectSchema

def modify_fti(fti):
    folder_modify_fti(fti, allowed=('PSCReleaseFolder',
                                    'PSCImprovementProposalFolder',
                                    'HelpCenterFAQFolder',
                                    'HelpCenterHowToFolder',
                                    'HelpCenterTutorialFolder',
                                    'HelpCenterErrorReferenceFolder',
                                    'HelpCenterLinkFolder',
                                    'HelpCenterGlossary',
                                    'HelpCenterInstructionalVideoFolder',
                                    'HelpCenterReferenceManualFolder'
                                    #'Collector',
                                    ),
                      global_allow=0)


class PSCProject(OrderedBaseFolder):
    """Package class that holds the information about the Software Project.
    """

    __implements__ = (OrderedBaseFolder.__implements__,)

    archetype_name = 'Software Project'
    immediate_view = default_view = 'psc_project_view'
    content_icon = 'product_icon.gif'
    schema = PSCProjectSchema

    security = ClassSecurityInfo()

    actions = (
        {
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/psc_project_view',
            'permissions': (CMFCorePermissions.View,),
        },
        {
            'id': 'sharing',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,),
        },
    )

    typeDescMsgId = 'description_edit_package'
    typeDescription = ('A Software Project contains details about a '
                       'particular software package. It can keep track '
                       'of meta-data about the project, as well as '
                       'releases and improvement proposals.')

    security.declarePrivate('validate_id')
    def validate_id(self, value):
        """Ensure that we don't get a value that is the same as the id of a
        category. This will break our nice acquisition-fuelled listing templates
        and generally be bad.
        """
        if value in self.getAvailableCategoriesAsDisplayList().keys():
            return "Short name %s is invalid - " \
                   "it is the same as the name of a project category" % (value,)
        else:
            return None

    security.declarePrivate('initializeArchetype')
    def initializeArchetype(self, **kwargs):
        """Initialize package.

        Packages are initialized with a release folder and a roadmap.
        """
        OrderedBaseFolder.initializeArchetype(self,**kwargs)
        if not self.objectIds('PSCReleaseFolder'):
            self.invokeFactory('PSCReleaseFolder', config.RELEASES_ID)
        if not self.objectIds('PSCImprovementProposalFolder'):
            self.invokeFactory('PSCImprovementProposalFolder',
                               config.IMPROVEMENTS_ID)

    security.declareProtected(CMFCorePermissions.View, 'sort_title')
    def sort_title(self):
        """Get the sort-order title. Used in a catalog index to sort the
        title of the item with human ordering.
        """
        return self.title_or_id().strip().lower()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent,
                              'setCategories')
    def setCategories(self, value):
        """Overrides categories mutator so we can reindex internal content.
        """
        self.getField('categories').set(self, value)
        self.reindexObject(idxs=['getCategories'])
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(
                          portal_type=['PSCRelease',
                                       'PSCFile',
                                       'PSCFileLink',
                                       'PSCImprovementProposal'],
                          path='/'.join(self.getPhysicalPath()))
        for r in res:
            o = r.getObject()
            o.reindexObject(idxs=['getCategories'])

    security.declareProtected(CMFCorePermissions.View, 'getCategoryTitles')
    def getCategoryTitles(self):
        """Return selected categories as a list of category long names,
        for the user interface.
        """
        vocab = self.getCategoriesVocab()
        values = [vocab.getValue(c) for c in self.getCategories()]
        values.sort()
        return values

    security.declareProtected(CMFCorePermissions.View, 'getCategoriesVocab')
    def getCategoriesVocab(self):
        """Get categories vocabulary from parent package area via acquisition.
        """
        return self.getAvailableCategoriesAsDisplayList()

    security.declareProtected(CMFCorePermissions.View, 'getReleaseFolder')
    def getReleaseFolder(self):
        """Get the release folder.

        We only should have one, so only deal with case of single
        folder. This is created when we're created, so we should always
        have one.
        """
        return self.contentValues('PSCReleaseFolder')[0]

    security.declareProtected(CMFCorePermissions.View, 'getRoadmapFolder')
    def getRoadmapFolder(self):
        """Get the roadmap folder.

        We only should have one, so only deal with case of single
        folder. This is created when we're created, so we should always
        have one.
        """
        return self.contentValues('PSCImprovementProposalFolder')[0]

    security.declareProtected(CMFCorePermissions.View, 'getLatestRelease')
    def getLatestRelease(self):
        """Get the most recent release, or None if none can be found. Will
        prefer releases of the preferred maturity set in the software center.
        """
        release_folder = self.getReleaseFolder()
        catalog = getToolByName(self, 'portal_catalog')

        preferredMaturity = self.getPreferredMaturity()

        res = []

        if preferredMaturity:
            res = catalog.searchResults(
                            path = '/'.join(release_folder.getPhysicalPath()),
                            review_state = 'published',
                            getMaturity = preferredMaturity,
                            sort_on = 'effective',
                            sort_order = 'reverse',
                            portal_type = 'PSCRelease')

        if not res:
            res = catalog.searchResults(
                            path = '/'.join(release_folder.getPhysicalPath()),
                            review_state = 'published',
                            sort_on = 'effective',
                            sort_order = 'reverse',
                            portal_type = 'PSCRelease')

        if not res:
            return None
        else:
            return res[0].getObject()

    security.declareProtected(CMFCorePermissions.View, 'getAdditionalContainedResources')
    def getAdditionalContainedResources(self, ignore=('PSCReleaseFolder', 
                                            'PSCImprovementProposalFolder',)):
        """
        Get any contained resources (objects) not of the types in the list of
        ignored types passed in. This essentially allows access to contained
        help-center items, collectors etc.
        """
        return [o for o in self.folderlistingFolderContents() \
                    if o.portal_type not in ignore]

    security.declareProtected(CMFCorePermissions.View, 'getNotAddableTypes')
    def getNotAddableTypes(self):
        """Hide the release container types if it already exists.
        """
        ignored = []
        if config.RELEASES_ID in self.objectIds():
            ignored.append('PSCReleaseFolder')
        if config.IMPROVEMENTS_ID in self.objectIds():
            ignored.append('PSCImprovementProposalFolder')
        return ignored

    security.declareProtected(CMFCorePermissions.AddPortalContent, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Override for the .py script in portal_scripts with the same name.
        Gives some default names for contained content types:

            PSCImprovementProposalFolder: 'improvement'
            PSCReleaseFolder: 'release'
            HelpCenterFAQFolder: 'faq'
            HelpCenterHowToFolder: 'how-to'
            HelpCenterTutorialFolder: 'tutorial'
            HelpCenterErrorReferenceFolder: 'error'
            HelpCenterLinkFolder: 'link'
            HelpCenterGlossary: 'glossary'
            HelpCenterInstructionalVideoFolder: 'video'
            #Collector: 'collector'

        for all other types, falls back on the aq parent.
        """

        consideredTypes = {
            'PSCImprovementProposalFolder': config.IMPROVEMENTS_ID,
            'PSCReleaseFolder': config.RELEASES_ID,
            'HelpCenterFAQFolder': 'faq',
            'HelpCenterHowToFolder': 'how-to',
            'HelpCenterTutorialFolder': 'tutorial',
            'HelpCenterErrorReferenceFolder': 'error',
            'HelpCenterLinkFolder': 'link',
            'HelpCenterGlossary': 'glossary',
            'HelpCenterInstructionalVideoFolder': 'video',
            #'Collector': 'collector'
            }

        # Use aq parent if we don't know what to do with the type
        if type_name not in consideredTypes:
            return self.aq_inner.aq_parent.generateUniqueId(type_name)
        else:
            return self._ensureUniqueId(consideredTypes[type_name])

    security.declarePrivate('_ensureUniqueId')
    def _ensureUniqueId(self, id):
        """Test the given id. If it's not unique, append .<n> where n is a
        number to make it unique.
        """
        if id in self.objectIds():
            idx = 0
            while '%s.%d' % (id, idx) in self.objectIds():
                idx += 1
            return '%s.%d' % (id, idx)
        else:
            return id

    security.declareProtected(CMFCorePermissions.View, 'getProjectURL')
    def getProjectURL(self):
        """Return URL to this project. Child items can use this."""
        return self.absolute_url()

    security.declareProtected(CMFCorePermissions.View, 'getVersionsVocab')
    def getVersionsVocab(self):
        """To ensure PloneHelpCenter integration works, return the versions
        defined, by looking at the versions found in the releases.
        """
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(portal_type = 'PSCRelease',
                                         path = '/'.join(self.getPhysicalPath()))
        return [r.getId for r in releases if r]


registerType(PSCProject, config.PROJECTNAME)
