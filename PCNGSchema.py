"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: PCNGSchema.py,v 1.20 2004/09/11 17:05:54 ajung Exp $
"""

from Globals import InitializeClass 
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions

from Products.Archetypes.public import ManagedSchema

class PCNGSchema(ManagedSchema):
    """ We wrap the ManagedSchema class in case we need something
        special.
    """

    security = ClassSecurityInfo()

InitializeClass(PCNGSchema)

