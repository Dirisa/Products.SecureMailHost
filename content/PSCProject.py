"""
$Id: PSCProject.py,v 1.2 2005/03/01 21:39:01 limi Exp $
"""

from Products.Archetypes.public import OrderedBaseFolder
from Products.Archetypes.public import registerType
from Products.Archetypes.public import DisplayList

from Products.PloneSoftwareCenter.config import *
from Products.PloneSoftwareCenter.factory import factoryRegistry
from Products.PloneSoftwareCenter.factory import getFactory
from Products.PloneSoftwareCenter.utils import folder_modify_fti

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

from schemata import PSCProjectSchema

from AccessControl import ClassSecurityInfo

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
    """ Package class that holds the information about the Software Project """

    __implements__ = (OrderedBaseFolder.__implements__,)

    archetype_name = 'Software Project'
    immediate_view = default_view = 'psc_project_view'
    content_icon = 'product_icon.gif'
    schema = PSCProjectSchema
    
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/psc_project_view',
        'permissions' : (CMFCorePermissions.View,)
         },{
        'id'          : 'sharing',
        'name'        : 'Sharing',
        'action'      : 'string:${object_url}/folder_localrole_form',
        'permissions' : (CMFCorePermissions.ManageProperties,)
         },
         )


    typeDescription= 'A Software Project contains details about a particular software package. It can keep track of meta-data about the project, as well as releases and improvement proposals.'
    typeDescMsgId  = 'description_edit_package'

    security = ClassSecurityInfo ()

    def initializeArchetype(self, **kwargs):
        """Initialize package.

        Packages are initialized with a release folder and a roadmap
        """
        OrderedBaseFolder.initializeArchetype(self,**kwargs)

        if not  self.objectIds('PSCReleaseFolder'):
            self.invokeFactory( 'PSCReleaseFolder'
                , RELEASES_ID
                )
                
        if not  self.objectIds('PSCImprovementProposalFolder'):
            self.invokeFactory( 'PSCImprovementProposalFolder'
                , IMPROVEMENTS_ID
                )

    def _get_settings(self):
        facts = [(k, v.description) for k, v in
                 factoryRegistry.items()]
        return DisplayList(facts)

    def getCategoriesVocab(self):
        """Get categories vocabulary from parent package area via acquisition
        """
        return DisplayList ([(item, item) for item in \
                                self.getAvailableCategories ()])

    def enableSettings(self, settings):
        current = list(self.getSettings())
        settings = list(settings)
        # Keep previously enabled settings in
        # addition to the current ones. The effect is
        # that you can't disable settings.
        settings.extend(filter(lambda x: x not in settings, current))
        self.Schema()['settings'].set(self, settings)
        settings = self.getSettings()
        for name in settings:
            factory = getFactory(name, None)
            if factory is None:
                raise ValueError, ('Non-existing factory '
                                   'named %s' % name)
            factory(self)

    def getReleaseFolder(self):
        """Get the release folder.

        We only should have one, so only deal with case of single
        folder. This is created when we're created, so we should always
        have one.
        """

        return self.contentValues('PSCReleaseFolder')[0]

    def getRoadmapFolder(self):
        """Get the roadmap folder.

        We only should have one, so only deal with case of single
        folder. This is created when we're created, so we should always
        have one.
        """

        return self.contentValues('PSCImprovementProposalFolder')[0]
        
    def getLatestRelease(self):
        release_folder = self.getReleaseFolder()
        releases = release_folder.contentValues('PSCRelease')

        if not releases:
            return None
        releases.sort(
            lambda a,b:cmp(a.getEffectiveDate(), b.getEffectiveDate())
            )
        return releases[-1]
        
    
    security.declareProtected (ADD_CONTENT_PERMISSION, 'generateUniqueId')
    def getNotAddableTypes(self):
        """Hide the release container types if it already exists
        """
        
        ignored = []
            
        if RELEASES_ID in self.objectIds ():
            ignored.append ('PSCReleaseFolder')
            
        if IMPROVEMENTS_ID in self.objectIds ():
            ignored.append ('PSCImprovementProposalFolder')
            
        return ignored
    
        
    security.declareProtected (ADD_CONTENT_PERMISSION, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Override for the .py script in portal_scripts with the same name.
        Gives some default names for contained content types:
        
            PSCImprovementProposalFolder: 'improvement'
            PSCReleaseFolder: 'release'
            HelpCenterFAQFolder: 'faq'
            HelpCenterHowToFolder: 'howto'
            HelpCenterTutorialFolder: 'tutorial'
            HelpCenterErrorReferenceFolder: 'error'
            HelpCenterLinkFolder: 'link'
            HelpCenterGlossary: 'glossary'
            HelpCenterInstructionalVideoFolder: 'video'
            #Collector: 'collector'
            
        for all other types, falls back on the aq parent.
        """
                        
        consideredTypes = {
            'PSCImprovementProposalFolder'              : IMPROVEMENTS_ID,
            'PSCReleaseFolder'                          : RELEASES_ID,
            'HelpCenterFAQFolder'                       : 'faq',
            'HelpCenterHowToFolder'                     : 'howto',
            'HelpCenterTutorialFolder'                  : 'tutorial',
            'HelpCenterErrorReferenceFolder'            : 'error',
            'HelpCenterLinkFolder'                      : 'link',
            'HelpCenterGlossary'                        : 'glossary',
            'HelpCenterInstructionalVideoFolder'        : 'video',
            #'Collector'                                 : 'collector'
            }
            
        # Use aq parent if we don't know what to do with the type
        if type_name not in consideredTypes:
            return self.aq_inner.aq_parent.generateUniqueId (type_name)
        else:
            return self._ensureUniqueId (consideredTypes[type_name])

    def _ensureUniqueId (self, id):
        """Test the given id. If it's not unique, append .<n> where n is a
        number to make it unique
        """
        
        if id in self.objectIds ():
            idx = 0
        
            while "%s.%d" % (id, idx) in self.objectIds ():
                idx += 1
                
            return "%s.%d" % (id, idx)
        else:
            return id

    def getProjectURL(self):
        """Return URL to this project. Child items can use this."""
        return self.absolute_url()
        
    def getVersions_vocab (self):
        """To ensure PloneHelpCenter integration works, return the versions
        defined, by looking at the versions found in the releases.
        """
        
        catalog = getToolByName (self, 'portal_catalog')
        
        releases = catalog.searchResults (portal_type = 'PSCRelease',
                                          path = self.getPhysicalPath ())
                                         
        return [r.getId for r in releases if r]

        

registerType(PSCProject, PROJECTNAME)
