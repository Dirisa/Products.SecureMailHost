from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

from Products.validation import validation
from validators import ExistingFolderPathValidator,ExternalMD5UtilityValidator
validation.register(ExistingFolderPathValidator('isValidExistingFolderPath'))
validation.register(ExternalMD5UtilityValidator('isValidExternalMD5Utility'))

def initialize(context):
    ##Import Types here to register them
    import PloneLocalFolderNG

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)
    
    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)


