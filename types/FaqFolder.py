#  This is a Plone FAQ Content type, with enhanced features
#  like deviding the FAQ into Sections, and Display relevant
#  versions.
#
#  Created by A. Hadi and J. Ladage of Zopeworks NL
# 


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

schema = BaseFolderSchema + Schema((
    TextField('description',
                widget=TextAreaWidget(description_msgid="desc_folder",
                                      description="The description of the FAQ.",
                                      label_msgid="label_folder",
                                      label="Description",
                                      i18n_domain = "faq",
                                      rows=6)),
    LinesField('versions',
                widget=LinesWidget(description="Define the available versions a FAQ can apply to.",
                                            label="Versions",
                                            i18n_domain = "faq",
                                            rows=6)),
                                      
    LinesField('sections',
                widget=LinesWidget(description="Define the available sections a FAQ can be assigned to.",
                                            label="Sections",
                                            i18n_domain = "faq",
                                            rows=6)),
    ))
 

class HelpCenterFaqFolder(BaseFolder):
    """A simple folderish archetype"""
    schema = schema
    archetype_name = 'FAQ Container'
    meta_type = 'HelpCenterFaqFolder'
    filter_content_types = 1
    allowed_content_types = ('HelpCenterFaqEntry')
    
    
    def _get_versions_vocab(self):
        return self.versions

    def _get_sections_vocab(self):
        return self.sections
    
registerType(HelpCenterFaqFolder)
