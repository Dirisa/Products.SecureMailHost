from Products.CMFCore.CMFCorePermissions import AddPortalContent

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneHelpCenter"
SKINS_DIR = 'skins'

GLOBALS = globals()

DEFAULT_CONTENT_TYPES = {
    'default_output_type': 'text/html',
    'default_content_type': 'text/restructured',
    'allowable_content_types': ('text/restructured',
                                'text/html',
                                'text/structured',)
    }
