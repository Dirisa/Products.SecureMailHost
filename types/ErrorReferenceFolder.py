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
from schemata import ErrorReferenceFolderSchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.ErrorReferenceFolder')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterErrorReferenceFolder')
def addHelpCenterErrorReferenceFolder(self, id, **kwargs):
    o = HelpCenterErrorReferenceFolder(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterErrorReferenceFolder(PHCFolder,BaseFolder):
    """A simple folderish archetype"""

    content_icon = 'errorref_icon.gif'

    schema = ErrorReferenceFolderSchema
    archetype_name = 'Error Reference Section'
    meta_type = 'HelpCenterErrorReferenceFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterErrorReference', )
    
    typeDescription= 'An Error Reference Section can contain references to and explanations of common errors.'
    typeDescMsgId  = 'description_edit_errorreferencefolder'

    
    security = ClassSecurityInfo()
    
    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/errorreferencefolder_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    )

registerType(HelpCenterErrorReferenceFolder, PROJECTNAME)
