from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.PloneHelpCenter.config import *
from schemata import ReferenceManualPageSchema
from PHCContent import PHCContent

class HelpCenterReferenceManualPage(PHCContent,BaseContent):
    """Part of a reference manual."""

    __implements__ = (PHCContent.__implements__,
                      BaseContent.__implements__,)

    schema = ReferenceManualPageSchema
    archetype_name = 'Page'
    meta_type='HelpCenterReferenceManualPage'
    content_icon = 'referencemanual_icon.gif'

    global_allow = 0
    allow_discussion = 1

    typeDescription= 'A Reference Manual Page contains the text of one of the pages of the the reference manual, usually confined to a single topic.'
    typeDescMsgId  = 'description_edit_referencemanualpage'


    actions = (
        {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${object_url}/referencemanualpage_view',
            'permissions' : (CMFCorePermissions.View,)
        },
        {
            'id'          : 'local_roles',
            'name'        : 'Sharing',
            'action'      : 'string:${object_url}/folder_localrole_form',
            'permissions' : (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions


registerType(HelpCenterReferenceManualPage, PROJECTNAME)
    
