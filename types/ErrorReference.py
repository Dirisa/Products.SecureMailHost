from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import ErrorReferenceSchema
from PHCContent import PHCContent


class HelpCenterErrorReference(PHCContent,OrderedBaseFolder):
    """This is an error reference object, meant to hold documentation about error messages""" 

    __implements__ = (PHCContent.__implements__,
                      OrderedBaseFolder.__implements__,)


    content_icon = 'errorref_icon.gif'

    schema = ErrorReferenceSchema
    archetype_name = 'Error Reference'
    meta_type = 'HelpCenterErrorReference'
    global_allow = 0
    filter_content_types = 1
    allow_discussion = IS_DISCUSSABLE
    allowed_content_types = ('Image', 'File', 'PloneImage', 'PloneFile', )

    actions = ({
            'id': 'view',
            'name': 'View',
            'action': 'string:${object_url}/errorreference_view',
            'permissions': (CMFCorePermissions.View,)
        },
        {
            'id': 'attachments',
            'name': 'Attachments',
            'action': 'string:${object_url}/howto_attachments',
            'permissions': (CMFCorePermissions.ModifyPortalContent,)
        },
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions

    security = ClassSecurityInfo()
    
    security.declareProtected(CMFCorePermissions.View,'Versions')
    #

registerType(HelpCenterErrorReference, PROJECTNAME)
