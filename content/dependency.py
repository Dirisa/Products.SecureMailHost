"""
$Id: dependency.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""

from Products.Archetypes.public import BaseContent, registerType
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

from Products.PSCProject.config import *
from Products.PSCProject.utils import std_modify_fti
from schemata import APDependencySchema

def modify_fti(fti):
    std_modify_fti(fti)

class PSCProjectDependency(BaseContent):
    """Keeps track of dependencies."""
    archetype_name = 'Software Dependency'

    schema = APDependencySchema
    
    def setPackage(self, value):
        # XXX validateDependency comes from
        # the Release, but could be overriden
        # somewere.
        self.validateDependency(value)
        self.Schema()['package'].set(self, value)

    def _get_dependencies(self):
        return DEPENDENCY_TYPES

# XXX: Disabled for now, since this is not being actively developed
# registerType(PSCProjectDependency, PROJECTNAME)

