from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HowToSchema
from PHCContent import PHCContent
from AccessControl import ClassSecurityInfo
#from Products.ATContentTypes.types.ATContentType import translateMimetypeAlias
            
MAPPING = {'text_html' : 'text/html'}

class HelpCenterHowTo(PHCContent,BaseFolder):
    """This is a howto document content object, to which you can attach images and
    files.
    """

    __implements__ = (PHCContent.__implements__,
                      BaseFolder.__implements__,)
                         
    content_icon = 'howto_icon.gif'

    typeDescription= 'A How-to is a document describing how to address a single, common use-case or issue. You may add images and files as attachments.'
    typeDescMsgId  = 'description_edit_howto'


    schema = HowToSchema
    archetype_name = 'How-to'
    meta_type = 'HelpCenterHowTo'
    global_allow = 0
    filter_content_types = 1
    allow_discussion = IS_DISCUSSABLE
    allowed_content_types = ('Image', 'File', 'PloneImage', 'PloneFile', )

    actions = (
        {  
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
        {
            'id': 'local_roles',
            'name': 'Sharing',
            'action': 'string:${object_url}/folder_localrole_form',
            'permissions': (CMFCorePermissions.ManageProperties,)
        },
    ) + PHCContent.actions
        
    security = ClassSecurityInfo()
        
   
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setFormat')
    def setFormat(self, value):
        value = MAPPING.get(value, value)
        BaseFolder.setFormat(self, value)

registerType(HelpCenterHowTo, PROJECTNAME)
