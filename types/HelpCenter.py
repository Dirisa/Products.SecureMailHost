#
# The Plone Help Center container.
#
# A Help Center is pre-populated with the following folders:
#
# /faq - contains the FAQ objects
# /howto - contains the How-tos
# /tutorial - contains the tutorials
#
# The main goals of these folders are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HCRootSchema

class HelpCenter(BaseFolder):
    """A simple folderish archetype"""
    schema = HCRootSchema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/helpcenter_view',
        'permissions': (CMFCorePermissions.View,)
        },)
    content_icon = 'book_icon.gif'

    archetype_name = 'Help Center'
    meta_type = 'HelpCenter'
    filter_content_types = 1
    allowed_content_types = ('HelpCenterFAQFolder', 'HelpCenterHowToFolder', 'HelpCenterTutorialFolder')

    security = ClassSecurityInfo()

    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/helpcenter_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )

    def _get_versions_vocab(self):
        return self.versions

    def initializeArchetype(self, **kwargs):
        # prepopulate folder
        BaseFolder.initializeArchetype(self,**kwargs)

        self.invokeFactory('HelpCenterFAQFolder','faq')
        self['faq'].setTitle('FAQs')
        self['faq'].setDescription('Frequently Asked Questions.')

        self.invokeFactory('HelpCenterHowToFolder','howto')
        self['howto'].setTitle('How-tos')
        self['howto'].setDescription('Step-by-step instructions.')

        self.invokeFactory('HelpCenterTutorialFolder','tutorial')
        self['tutorial'].setTitle('Tutorials')
        self['tutorial'].setDescription('Detailed tutorials.')

registerType(HelpCenter, PROJECTNAME)
