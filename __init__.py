"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: __init__.py,v 1.5 2003/11/01 17:03:25 ajung Exp $
"""

from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
import os, os.path

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    ##Import Types here to register them
    import Collector
    import Issue

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

