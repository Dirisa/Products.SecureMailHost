from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import InstructionalVideoSchema
from PHCContent import PHCContent
from AccessControl import ClassSecurityInfo
#from Products.ATContentTypes.types.ATContentType import translateMimetypeAlias

MAPPING = {'text_html' : 'text/html'}

class HelpCenterInstructionalVideo(PHCContent,BaseContent):
    """This is an Instructional Video content type, to which you can attach 
    movies and other relevant files.
    """

    content_icon = 'movie_icon.gif'

    schema = InstructionalVideoSchema
    archetype_name = 'Video'
    meta_type = 'HelpCenterInstructionalVideo'
    global_allow = 0
    allow_discussion = IS_DISCUSSABLE
    
    typeDescription= 'An Instructional Video can be used to upload Flash instructional videos.'
    typeDescMsgId  = 'description_edit_instructionalvideo'


    actions = ({'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/ivideo_view',
                'permissions': (CMFCorePermissions.View,)
                },       
              )
        
    security = ClassSecurityInfo()
        
   
registerType(HelpCenterInstructionalVideo, PROJECTNAME)
