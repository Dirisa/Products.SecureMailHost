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
