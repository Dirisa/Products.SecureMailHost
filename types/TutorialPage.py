from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *

schema = BaseSchema + Schema((
    TextField('description',
              default='',
              searchable=1,
              accessor="Description",
              storage=MetadataStorage(),
              widget = TextAreaWidget(
    description = "Enter a brief description", 
    description_msgid = "help_description",
    label = "Description",
    label_msgid = "label_description",
    rows = 5,
    i18n_domain = "plone")),
    
    TextField('text',
              required = 1,
              searchable = 1,
              primary = 1,
              
              widget = RichWidget(
    description = "The body text.",
    description_msgid = "help_body_text",
    label = "Body text",
    label_msgid = "label_body_text",
    rows = 25,
    i18n_domain = "plone"),
    **DEFAULT_CONTENT_TYPES))
                             )

class HelpCenterTutorialPage(BaseContent):
    """Part of a tutorial."""

    schema = schema
    archetype_name = 'Tutorial Page'
    meta_type='HelpCenterTutorialPage'
    global_allow = 0

registerType(HelpCenterTutorialPage, PROJECTNAME)
    
