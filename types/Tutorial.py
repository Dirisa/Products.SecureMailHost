from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *

class HelpCenterTutorial(OrderedBaseFolder):
    """A tutorial containing TutorialPages, Files and Images."""

    archetype_name = 'Tutorial'
    meta_type='HelpCenterTutorial'
    content_icon = 'tutorial_icon.gif'

    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorialPage', 'Image', 'File')

registerType(HelpCenterTutorial, PROJECTNAME)
    
