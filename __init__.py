"""
$Id: __init__.py,v 1.3 2005/03/11 17:43:29 optilude Exp $
"""

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import listTypes
from Products.Archetypes.public import process_types

from Products.PloneSoftwareCenter import config
from Products.PloneSoftwareCenter import permissions


registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):

    # Allow import of config at ZPT/PythonScript
    from AccessControl import allow_module
    allow_module('Products.PloneSoftwareCenter.config')

    # Kick content registration
    from Products.PloneSoftwareCenter import content

    allTypes = listTypes(config.PROJECTNAME)

    # Register Archetypes content with the machinery
    content_types, constructors, ftis = process_types(
        allTypes, config.PROJECTNAME)

    member_content_types = []
    member_constructors  = []
    manager_content_types = []
    manager_constructors  = []

    for i in range(len(allTypes)):
        aType = allTypes[i]
        if aType['klass'] in ('PloneSoftwareCenter',):
            manager_content_types.append(content_types[i])
            manager_constructors.append(constructors[i])
        else:
            member_content_types.append(content_types[i])
            member_constructors.append(constructors[i])

    # other
    ContentInit(
        config.PROJECTNAME + ' Center',
        content_types = tuple(manager_content_types),
        permission = permissions.ADD_CONTENT_PERMISSION,
        extra_constructors = tuple(manager_constructors),
        fti = ftis,
        ).initialize(context)

    # topics
    ContentInit(
        config.PROJECTNAME + ' Project Content',
        content_types = tuple(member_content_types),
        permission = CMFCorePermissions.AddPortalContent,
        extra_constructors = tuple(member_constructors),
        fti = ftis,
        ).initialize(context)