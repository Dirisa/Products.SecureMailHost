#
#  This is the Plone Help Center FAQ Folder type, with enhanced features
#  like dividing the FAQ into Sections, and Display relevant
#  versions.
#


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import FAQFolderSchema
from PHCFolder import PHCFolder

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
