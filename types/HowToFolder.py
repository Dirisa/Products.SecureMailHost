#
# The Plone How-to container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HowToFolderSchema
from PHCFolder import PHCFolder



class HelpCenterHowToFolder(PHCFolder,BaseFolder):
    """A simple folderish archetype"""

    content_icon = 'topic_icon.gif'

    schema = HowToFolderSchema
    archetype_name = 'How-to Area'
    meta_type = 'HelpCenterHowToFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterHowTo', )
    
    security = ClassSecurityInfo()
    
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/howtofolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )

registerType(HelpCenterHowToFolder, PROJECTNAME)
