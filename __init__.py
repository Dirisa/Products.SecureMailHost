"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: __init__.py,v 1.19 2004/05/26 16:26:26 ajung Exp $
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

def initialize(context):

    ##Import Types here to register them
    import Collector, Issue

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


    # Install workflow factories
    from Products.PloneCollectorNG.workflows import pcng_issue_workflow
    from Products.PloneCollectorNG.workflows import pcng_simple_workflow

from Products.PythonScripts.Utility import allow_module
allow_module('textwrap')
allow_module('group_assignment_policies')
allow_module('base64')

##########################################################################
# Monkeypatch CMFCore.FSMetadata to ensure that security settings in
# ,metadata files are treated correct
##########################################################################

def _securityParser(self, data):
    """ A specific parser for security lines

    Security lines must be of the format

    (0|1):Role[,Role...]

    Where 0|1 is the acquire permission setting
    and Role is the roles for this permission
    eg: 1:Manager or 0:Manager,Anonymous
    """
    if data.find(':') < 1:
        raise ValueError, "The security declaration of file " + \
              "%r is in the wrong format" % self._filename

    acquire, roles = data.split(':')
    roles = [r.strip() for r in roles.split(',') if r.strip()]
    return (int(acquire), roles)

from Products.CMFCore.FSMetadata import FSMetadata
FSMetadata._securityParser = _securityParser
from zLOG import LOG, INFO
LOG('plonecollectorng', INFO, 'FSMetadata._securityParser() has been patched for security reasons')

