#
# The Plone How-to container.
#
# The main goals of these containers are to restrict the addable types and
# provide a sensible default view out-of-the-box, like the FAQ view.
#


from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.PloneHelpCenter.config import *

schema = BaseFolderSchema + Schema((
    TextField('description',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget=TextAreaWidget(description_msgid="desc_folder",
                                    description="Description for the Tutorial Container.",
                                    label_msgid="label_folder",
                                    label="Description",
                                    i18n_domain = "plonehelpcenter",
                                    rows=6)),
    LinesField('sections',
               default=['General'],
               widget=LinesWidget(
    label="Sections",
    description="Define the available sections a How-to can be assigned to.",
    i18n_domain="plonehelpcenter",
    rows=6)
               ),
    ))



class HelpCenterTutorialFolder(BaseFolder):
    """A simple folderish archetype"""

    content_icon = 'tutorial_icon.gif'

    schema = schema
    archetype_name = 'Tutorial Area'
    meta_type = 'HelpCenterTutorialFolder'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorial', )
    
    security = ClassSecurityInfo()
    
registerType(HelpCenterTutorialFolder, PROJECTNAME)
