"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Base.py,v 1.17 2004/09/11 15:31:39 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from Products.CMFCore.CMFCorePermissions import View

class ParentManagedSchema:
    """ mix-in class for AT content-types whose schema is managed by
        the parent container and retrieved through acquisition.
    """

    security = ClassSecurityInfo()    

    security.declareProtected(View, 'Schema')
    def Schema(self):
        """ retrieve schema from parent object """

        schema = getattr(self, '_v_schema', None)
        if schema is None:
            schema = self._v_schema = self.aq_parent.atse_getSchema()

        return ImplicitAcquisitionWrapper(self._v_schema, self)

InitializeClass(ParentManagedSchema)
