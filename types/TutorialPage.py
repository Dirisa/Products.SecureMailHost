from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *

schema = BaseSchema + Schema((
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
    
