#
# The Plone Instructional Video container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import InstructionalVideoFolderSchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.InstructionalVideoFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterInstructionalVideoFolder')
def addHelpCenterInstructionalVideoFolder(self, id, **kwargs):
    o = HelpCenterInstructionalVideoFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterInstructionalVideoFolder(PHCFolder,OrderedBaseFolder):
    """A simple folderish archetype"""

    content_icon = 'movie_icon.gif'

    schema = InstructionalVideoFolderSchema
    archetype_name = 'Video Section'
    meta_type = 'HelpCenterInstructionalVideoFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterInstructionalVideo', )
    
    security = ClassSecurityInfo()
    
    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/ivideofolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )

registerType(HelpCenterInstructionalVideoFolder, PROJECTNAME)
