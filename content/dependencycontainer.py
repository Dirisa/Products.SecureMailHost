"""
$Id: dependencycontainer.py,v 1.1 2005/02/28 05:10:36 limi Exp $
"""

from Products.Archetypes.public import OrderedBaseFolder, registerType
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

from Products.PSCProject.config import *
from Products.PSCProject.utils import folder_modify_fti


def modify_fti(fti):
    folder_modify_fti(fti, allowed=('PSCProjectDependency',))


class PSCProjectDependencyContainer(OrderedBaseFolder, UniqueObject):
    id = DEPENDENCIES
    archetype_name = 'Dependency Container'
    security = ClassSecurityInfo()


# XXX: Disabled for now, since this is not being actively developed
# registerType(PSCProjectDependencyContainer, PROJECTNAME)
