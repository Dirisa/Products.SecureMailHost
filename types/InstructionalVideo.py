from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import InstructionalVideoSchema
from PHCContent import PHCContent
from AccessControl import ClassSecurityInfo
#from Products.ATContentTypes.types.ATContentType import translateMimetypeAlias

MAPPING = {'text_html' : 'text/html'}

class HelpCenterInstructionalVideo(PHCContent,BaseFolder):
    """This is an Instructional Video content type, to which you can attach 
    movies and other relevant files.
    """

    content_icon = 'movie_icon.gif'

    schema = InstructionalVideoSchema
    archetype_name = 'Video'
    meta_type = 'HelpCenterInstructionalVideo'
    global_allow = 0
    filter_content_types = 1
    allow_discussion = IS_DISCUSSABLE
    allowed_content_types = ('Image', 'File', 'PloneImage', 'PloneFile', )

    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/ivideo_view',
                'permissions': (CMFCorePermissions.View,)
                },
        {
        'id': 'attachments',
        'name': 'Files',
        'action': 'string:${object_url}/ivideo_attachments',
        'permissions': (CMFCorePermissions.ModifyPortalContent,)
        },
        
        )
        
    security = ClassSecurityInfo()
        
   
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setFormat')
    def setFormat(self, value):
        value = MAPPING.get(value, value)
        BaseFolder.setFormat(self, value)

registerType(HelpCenterInstructionalVideo, PROJECTNAME)
