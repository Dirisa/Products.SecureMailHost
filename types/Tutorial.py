from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *

schema = BaseSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
                 description = 'A summary of the tutorial -  aims and scope. Will be displayed on every page of the tutorial.', 
                 description_msgid = "help_tutorial_summary",
                 label = "Tutorial Description",
                 label_msgid = "label_tutorial_description",
                 rows = 5,
                 i18n_domain = "plonehelpcenter")
    ),
))

class HelpCenterTutorial(OrderedBaseFolder):
    """A tutorial containing TutorialPages, Files and Images."""

    schema = schema
    archetype_name = 'Tutorial'
    meta_type='HelpCenterTutorial'
    content_icon = 'tutorial_icon.gif'

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorialPage', 'Image', 'File')

    def getTutorialDescription(self):
        return self.Description()
    
registerType(HelpCenterTutorial, PROJECTNAME)
    
