from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *
from schemata import HowToSchema


class HelpCenterHowTo(BaseFolder):
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
    
    def _get_versions_vocab(self):
        return self.aq_parent._get_versions_vocab()
    
    def _get_sections_vocab(self):
        return self.aq_parent._get_sections_vocab()

    security.declareProtected(CMFCorePermissions.View,'Versions')
    #
    def Versions(self):
        """method to display the versions in a nicer way
        """

        # XXX is this really necessary? the widget supports this, doesn't it? ~limi
        result=""
        for version in self.versions:
            if result:
                result=result+", "+ version
            else:
                result=version
        return result


registerType(HelpCenterHowTo, PROJECTNAME)
