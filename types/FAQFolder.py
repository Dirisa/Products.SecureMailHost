#
#  This is the Plone Help Center FAQ Folder type, with enhanced features
#  like dividing the FAQ into Sections, and Display relevant
#  versions.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import FAQFolderSchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.FAQFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterFAQFolder')
def addHelpCenterFAQFolder(self, id, **kwargs):
    o = HelpCenterFAQFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterFAQFolder(PHCFolder,OrderedBaseFolder):
    """A simple folderish archetype"""

    typeDescription= 'This is a folder that holds FAQs, and it allows you to display individual sections.'
    typeDescMsgId  = 'description_edit_faqfolder'

    content_icon = 'faq_icon.gif'

    schema = FAQFolderSchema
    archetype_name = 'FAQ Area'
    meta_type = 'HelpCenterFAQFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterFAQ', )
    
    security = ClassSecurityInfo()

    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/faqfolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )
    
registerType(HelpCenterFAQFolder, PROJECTNAME)