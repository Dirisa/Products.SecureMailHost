#
# The Plone Reference Manual container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import ReferenceManualFolderSchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.ReferenceManualFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterReferenceManualFolder')
def addHelpCenterReferenceManualFolder(self, id, **kwargs):
    o = HelpCenterReferenceManualFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterReferenceManualFolder(PHCFolder,OrderedBaseFolder):
    """A simple folderish archetype"""

    content_icon = 'referencemanual_icon.gif'

    schema = ReferenceManualFolderSchema
    archetype_name = 'Reference Manual Section'
    meta_type = 'HelpCenterReferenceManualFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterReferenceManual', )
    
    security = ClassSecurityInfo()
    
    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/referencemanualfolder_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id'          : 'local_roles',
            'name'        : 'Sharing',
            'action'      : 'string:${object_url}/folder_localrole_form',
            'permissions' : (CMFCorePermissions.ManageProperties,)
        },
    )


registerType(HelpCenterReferenceManualFolder, PROJECTNAME)
