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

    LinesField('sections',
               multiValued=1,
               required=1,
               vocabulary='_get_sections_vocab', # we acquire this from
                                                 # FAQFolder
               enforceVocabulary=1,
               widget=MultiSelectionWidget(
    label='Sections',
    description='Section(s) of the tutorials listing that this should appear in.',),
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

    # XXX - Why doesn't this show up in the edit form?
    typeDescription= 'A Tutorial can contain Tutorial Pages, Image and Files. Index order is decided by the folder order, use the normal up/down selectors to rearrange content.'
    typeDescMsgId  = 'description_edit_tutorial'
    
    
    def getTutorialDescription(self):
        """ Returns the description of the Tutorial - convenience method for TutorialPage """
        return self.Description()
    
registerType(HelpCenterTutorial, PROJECTNAME)
    
