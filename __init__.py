"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: __init__.py,v 1.11 2003/11/24 14:16:16 ajung Exp $
"""

import os, sys

from Globals import package_home
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from config import SKINS_DIR, GLOBALS, PROJECTNAME
from config import ADD_CONTENT_PERMISSION

d = os.path.dirname(__file__)
if not d in sys.path:
    sys.path.append(d)

registerDirectory(SKINS_DIR, GLOBALS)

import warnings
warnings.warn('\n\n'
'********************************************************\n'
'Reminder: PloneCollectorNG requires Archetypes 1.0.1. \n'
'Any other version is not supported yet!!!!\n'
'(This warning appears also with AT 1.0.1 installed)\n'
'********************************************************\n\n')

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



