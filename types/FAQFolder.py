#
#  This is the Plone Help Center FAQ Folder type, with enhanced features
#  like dividing the FAQ into Sections, and Display relevant
#  versions.
#


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *

schema = BaseFolderSchema + Schema((
    TextField('description',
                widget=TextAreaWidget(description_msgid="desc_folder",
                                      description="Description of the FAQ Container.",
                                      label_msgid="label_folder",
                                      label="Description",
                                      i18n_domain = "plonehelpcenter",
                                      rows=6)),
    LinesField('sections',
                widget=LinesWidget(description="Define the available sections a FAQ can be assigned to.",
                                            label="Sections",
                                            default="General",
                                            i18n_domain = "plonehelpcenter",
                                            rows=6)),
    ))
 

class HelpCenterFAQFolder(BaseFolder):
    """A simple folderish archetype"""

    content_icon = 'discussionitem_icon.gif'

    schema = schema
    archetype_name = 'FAQ Container'
    meta_type = 'HelpCenterFAQFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterFAQ', )
    
    security = ClassSecurityInfo()

    actions = ({
        'id'          : 'view',
        'name'        : 'View',
        'action'      : 'string:${object_url}/faqfolder_view',
        'permissions' : (CMFCorePermissions.View,)
         },
         )
    
    def _get_versions_vocab(self):
        return self.versions

    def _get_sections_vocab(self):
        return self.sections
    
registerType(HelpCenterFAQFolder, PROJECTNAME)
