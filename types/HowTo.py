from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HowToSchema
from PHCContent import PHCContent


class HelpCenterHowTo(PHCContent,BaseFolder):
    """This is a howto document content object, to which you can attach images and
    files.
    """

    content_icon = 'howto_icon.gif'

    schema = HowToSchema
    archetype_name = 'How-to'
    meta_type = 'HelpCenterHowTo'
    global_allow = 0
    filter_content_types = 1
    allow_discussion = 1
    allowed_content_types = ('Image', 'File', 'PloneImage', 'PloneFile', )

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'string:${object_url}/howto_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {
        'id': 'attachments',
        'name': 'Attachments',
        'action': 'string:${object_url}/howto_attachments',
        'permissions': (CMFCorePermissions.ModifyPortalContent,)
        },
        
        )

    security = ClassSecurityInfo()
    
    security.declareProtected(CMFCorePermissions.View,'Versions')
    #

registerType(HelpCenterHowTo, PROJECTNAME)
