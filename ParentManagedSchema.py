"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 T�bingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: ParentManagedSchema.py,v 1.1 2004/09/12 07:27:21 ajung Exp $
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

        # Schema() seems to be called during the construction phase when there is
        # not acquisition context. So we return the default schema itself.

        if not hasattr(self, 'aq_parent'): return self.schema

        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        schema = getattr(self, '_v_schema', None)
        if schema is None:
            schema = self._v_schema = self.aq_parent.atse_getSchema()

        return ImplicitAcquisitionWrapper(self._v_schema, self)

InitializeClass(ParentManagedSchema)
