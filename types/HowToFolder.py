#
# The Plone How-to container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions



schema = BaseFolderSchema + Schema((
    TextField('description',
                widget=TextAreaWidget(description_msgid="desc_folder",
                                      description="Description of the How-to Container.",
                                      label_msgid="label_folder",
                                      label="Description",
                                      i18n_domain = "plonehelpcenter",
                                      rows=6)),
    LinesField('sections',
                widget=LinesWidget(description="Define the available sections a How-to can be assigned to.",
                                            label="Sections",
                                            i18n_domain = "plonehelpcenter",
                                            rows=6)),
    ))



class HelpCenterHowToFolder(BaseFolder):
    """A simple folderish archetype"""

    content_icon = 'topic_icon.gif'

    schema = schema
    archetype_name = 'How-to Container'
    meta_type = 'HelpCenterHowToFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterHowTo')
    
registerType(HelpCenterHowToFolder)
