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

    content_icon = 'faq_icon.gif'

    schema = FAQFolderSchema
    archetype_name = 'FAQ Section'
    meta_type = 'HelpCenterFAQFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterFAQ', )
    
    security = ClassSecurityInfo()
    
        typeDescription= 'A FAQ Section can hold frequently asked questions with answers.'
    typeDescMsgId  = 'description_edit_faqfolder'

    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/faqfolder_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    )
    
registerType(HelpCenterFAQFolder, PROJECTNAME)
