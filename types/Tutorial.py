from Products.Archetypes.public import *
from Products.PloneHelpCenter.config import *
from schemata import TutorialSchema

class HelpCenterTutorial(OrderedBaseFolder):
    """A tutorial containing TutorialPages, Files and Images."""

    schema = TutorialSchema
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
    
