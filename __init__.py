"""
$Id: __init__.py,v 1.2 2005/03/09 18:04:32 dtremea Exp $
"""

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory

from Products.Archetypes.public import listTypes
from Products.Archetypes.public import process_types

from Products.PloneSoftwareCenter import config
from Products.PloneSoftwareCenter import permissions
#import Products.PloneSoftwareCenter.Extensions.Install

registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):

    # Allow import of config at ZPT/PythonScript
    from AccessControl import allow_module
    allow_module('Products.PloneSoftwareCenter.config')

    # Kick content registration
    from Products.PloneSoftwareCenter import content

    # Register Archetypes content with the machinery
    content_types, constructors, ftis = process_types(
        listTypes(config.PROJECTNAME), config.PROJECTNAME)

    ContentInit(
        config.PROJECTNAME + ' Content',
        content_types = content_types,
        permission = permissions.ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis).initialize(context)
