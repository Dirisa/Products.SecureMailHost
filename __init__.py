from Globals import package_home
from Products.Archetypes import process_types
from Products.Archetypes.debug import log
from Products.Archetypes import listTypes, registerType
from Products.Archetypes.utils import pathFor
from Products.CMFCore  import DirectoryView, utils
import os, os.path
import Products.CMFCore.CMFCorePermissions as CMFCorePermissions
from MemberPermissions import ADD_PERMISSION

PKG_NAME = "CMFMember"
SKIN_NAME = "member"
TYPE_NAME = "Member"  # Name of types_tool type used to hold member data

global GLOBALS
GLOBALS = globals()

DirectoryView.registerDirectory('skins', GLOBALS)

def initialize(context):
    import sys
    ##Import Types here to register them
    import types
    
    homedir = package_home(GLOBALS)
    target_dir = os.path.join(homedir, 'skins', SKIN_NAME)
    
    content_types, constructors, ftis = process_types(listTypes(PKG_NAME),
                                                      PKG_NAME)
    utils.ContentInit(
        '%s Content' % PKG_NAME,
        content_types      = content_types,
        permission         = ADD_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
    
    import MemberDataTool
    import RegistrationTool
    tools = (
        MemberDataTool.MemberDataTool,
        RegistrationTool.RegistrationTool,
        )

    import sys
    sys.stdout.write('tools = %s\n' % (str(tools)))
    utils.ToolInit(PKG_NAME + ' Tool', tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)
    sys.stdout.write('done\n')
    
