#
#  This is the Plone Help Center folderish Glossary type, which
#  is a simple container that has Definitions.
#

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import GlossarySchema
from PHCFolder import PHCFolder


# generate the add method ourselves so we can set the add permission
security = ModuleSecurityInfo('Products.PloneHelpCenter.Glossary')
security.declareProtected(ADD_HELP_AREA_PERMISSION, 'addHelpCenterGlossary')
def addHelpCenterGlossary(self, id, **kwargs):
    o = HelpCenterGlossary(id)
    self._setObject(id, o)
    o = getattr(self, id)
    o.initializeArchetype(**kwargs)


class HelpCenterGlossary(PHCFolder,OrderedBaseFolder):
    """A simple folderish archetype"""

    content_icon = 'glossary_icon.gif'

    schema = GlossarySchema
    archetype_name = 'Glossary'
    meta_type = 'HelpCenterGlossary'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterDefinition', )
    
    typeDescription= 'A Glossary can be used to hold definitions of common terms, listing them in a dictionary-like manner.'
    typeDescMsgId  = 'description_edit_glossary'
    
    security = ClassSecurityInfo()

    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/glossary_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    )
    
registerType(HelpCenterGlossary, PROJECTNAME)
