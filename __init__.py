"""
$Id: __init__.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""

# constants for archetypes
from config import *
import Extensions.Install

##############################################################
# basic imports
from Products.CMFCore import utils as cmf_utils
from Products.Archetypes.public import *
from Products.Archetypes import listTypes

#Archetypes I believe claims that it will registerDirectories
#for you.  I dont see any code in there that does that.
#I think it will do it when you Install/Uninstall but when
#you restart you are hosed.  This is jerking the users chain.

from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory(SKINS_DIR, globals())

def initialize(self, context=None):
    from AccessControl import allow_module
    allow_module('Products.PloneSoftwareCenter.config')
    
    # kick content registration
    from Products.PloneSoftwareCenter import content

    # register archetypes content with the machinery
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)

    cmf_utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis).initialize(self)
