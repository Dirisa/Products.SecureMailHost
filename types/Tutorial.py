from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *

class HelpCenterTutorial(OrderedBaseFolder):
    """A tutorial containing TutorialPages, Files and Images."""

    archetype_name = 'Tutorial'
    meta_type='HelpCenterTutorial'
    global_allow = 0
    filter_content_types = 1
    allowed_content_types = ('HelpCenterTutorialPage', 'Image', 'File')

registerType(HelpCenterTutorial, PROJECTNAME)
    
