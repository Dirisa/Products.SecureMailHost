#
# The Plone How-to container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import TutorialFolderSchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.TutorialFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterTutorialFolder')
def addHelpCenterTutorialFolder(self, id, **kwargs):
    o = HelpCenterTutorialFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterTutorialFolder(PHCFolder,OrderedBaseFolder):
    """A simple folderish archetype"""

    content_icon = 'tutorial_icon.gif'

    schema = TutorialFolderSchema
    archetype_name = 'Tutorial Section'
    meta_type = 'HelpCenterTutorialFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorial', )
    
    typeDescription= 'A Tutorial Section can contain tutorial-length, multi-page documentation.'
    typeDescMsgId  = 'description_edit_tutorialfolder'

    
    security = ClassSecurityInfo()
    
    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/tutorialfolder_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    )


registerType(HelpCenterTutorialFolder, PROJECTNAME)
