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
from schemata import TutorialFolderSchema
from PHCFolder import PHCFolder

class HelpCenterTutorialFolder(PHCFolder,BaseFolder):
    """A simple folderish archetype"""

    content_icon = 'tutorial_icon.gif'

    schema = TutorialFolderSchema
    archetype_name = 'Tutorial Area'
    meta_type = 'HelpCenterTutorialFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorial', )
    
    security = ClassSecurityInfo()
    
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/tutorialfolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )

registerType(HelpCenterTutorialFolder, PROJECTNAME)
