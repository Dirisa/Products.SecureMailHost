"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
D-72070 T�bingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: ParentManagedSchema.py,v 1.6 2004/09/27 12:39:15 spamsch Exp $
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
    def Schema(self, schema_id=None):
        """ Retrieve schema from parent object. The client class should
            override the method as Schema(self) and then call his method
            of the baseclass with the corresponding schema_id.
        """

        # Schema() seems to be called during the construction phase when there is
        # not acquisition context. So we return the default schema itself.

        if not hasattr(self, 'aq_parent'): return self.schema

        # If we're called by the generated methods we can not rely on
        # the id and need to check for portal_type
        if not self.aq_parent.atse_isSchemaRegistered(self.portal_type):
            return self.schema

        if not schema_id:
            schema_id = self.portal_type
            
        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        self._v_schema = getattr(self, '_v_schema', None)
        if self._v_schema is None:
            self._v_schema = self.aq_parent.atse_getSchemaById(schema_id)
            self.initializeArchetype()
            
            for field in self._v_schema.fields():

                ##########################################################
                # Fake accessor and mutator methods
                ##########################################################

                name = field.getName()

                def atse_get_method(self=self, name=name, *args, **kw):
                    return self.getField(name).get(self, **kw)

                setattr(self, '_v_%s_accessor' % name, atse_get_method )
                field.accessor = '_v_%s_accessor' % name
                field.edit_accessor = field.accessor

                def atse_set_method(value, self=self, name=name, *args, **kw):
                    if name != 'id':
                        self.getField(name).set(self, value, **kw)

                    # saving id directly (avoiding unicode problems)
                    else: self.setId(value)

                setattr(self, '_v_%s_mutator' % name, atse_set_method )
                field.mutator = '_v_%s_mutator' % name

                # Check if we need to update our own properties
                try:
                    value = field.get(self)
                    
                except:
                    field.set(self, field.default)

        return ImplicitAcquisitionWrapper(self._v_schema, self)

InitializeClass(ParentManagedSchema)
