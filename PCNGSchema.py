"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: PCNGSchema.py,v 1.19 2004/09/11 15:31:39 ajung Exp $
"""

from types import FileType

from Globals import InitializeClass, Persistent
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import *
from ZPublisher.HTTPRequest import FileUpload
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.utils import mapply
from Products.Archetypes.Layer import DefaultLayerContainer
from Products.Archetypes.interfaces.layer import ILayerContainer, ILayerRuntime, ILayer 
from Products.Archetypes.interfaces.field import IField, IImageField
from Products.Archetypes.interfaces.base import IBaseUnit
from Products.Archetypes.debug import log_exc

from Products.Archetypes.public import ManagedSchema

class PCNGSchema(ManagedSchema):
    """ We wrap the ManagedSchema class in case we need something
        special.
    """

    security = ClassSecurityInfo()

InitializeClass(PCNGSchema)

