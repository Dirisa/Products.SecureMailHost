from Products.CMFCore.CMFCorePermissions import AddPortalContent
from Products.Archetypes.public import DisplayList

ADD_CONTENT_PERMISSION = AddPortalContent
ADD_HELP_AREA_PERMISSION = 'PloneHelpCenter: Add Help Center Area'
PROJECTNAME = "PloneHelpCenter"
SKINS_DIR = 'skins'

GLOBALS = globals()

DEFAULT_CONTENT_TYPES = {
    'default_output_type': 'text/html',
    'default_content_type': 'text/html',
    'allowable_content_types': ('text/plain',
                                'text/restructured',
                                'text/html',
                                'text/structured',)
    }

IS_DISCUSSABLE=1

IMPORTANCE_VOCAB = DisplayList((
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ))
    
IMPORTANCE_DEFAULT = 'medium'

# References to other referenceable (usally Archetypes based) items in the 
# portal are disabled by default. By enabling them you'll get another Field in
# all PHCContent based types where you can select one or more items. In the view
# of those items at the bottom a 'see also' section shows the linked title and  
# the description of the target object. Only 'View'able objects are shown.
# another option is to use the new-style ATReferenceBrowserWidget. It will be 
# used if it is in your Products folder. You need to install it with 
# quickinstaller, otherwise the base_edit of PHCContent based types is broken.

ENABLE_REFERENCES = False
#ENABLE_REFERENCES = True

# here you can specify which types are allowed as references.
REFERENCEABLE_TYPES = ('HelpCenterFAQ',
    'HelpCenterDefinition',
    'HelpCenterTutorial',
    'HelpCenterErrorReference',
    'HelpCenterHowTo',
    'HelpCenterLink',
    #'Document'
)
