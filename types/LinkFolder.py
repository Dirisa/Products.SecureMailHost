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
security = ModuleSecurityInfo('Products.PloneHelpCenter.LinkFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterLinkFolder')
def addHelpCenterLinkFolder(self, id, **kwargs):
    o = HelpCenterLinkFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterLinkFolder(PHCFolder,BaseFolder):
    """A simple folderish archetype"""

    typeDescription= 'This is a folder that holds Help Center Links, and it allows you to display individual sections.'
    typeDescMsgId  = 'description_edit_linkfolder'

    content_icon = 'link_icon.gif'

    schema = FAQFolderSchema
    archetype_name = 'Link Area'
    meta_type = 'HelpCenterLinkFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterLink', )
    
    security = ClassSecurityInfo()

    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/helplinkfolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )
    
registerType(HelpCenterLinkFolder, PROJECTNAME)
