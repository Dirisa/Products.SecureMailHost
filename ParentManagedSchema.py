"""
ATSchemaEditorNG

(C) 2003,2004, Andreas Jung, ZOPYX Software Development and Consulting
and Contributors
D-72070 T�bingen, Germany

Contact: andreas@andreas-jung.com

License: see LICENSE.txt

$Id: ParentManagedSchema.py,v 1.12 2004/09/27 17:18:09 spamsch Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import ImplicitAcquisitionWrapper
from Products.CMFCore.CMFCorePermissions import View
from Products.Archetypes.Schema import ManagedSchema
from zLOG import LOG, INFO

from util import create_signature

class ParentManagedSchema:
    """ mix-in class for AT content-types whose schema is managed by
        the parent container and retrieved through acquisition.
    """

    security = ClassSecurityInfo()  

    def _wrap_schema(self, schema):
        return ImplicitAcquisitionWrapper(ManagedSchema(schema.fields()), self)

    security.declareProtected(View, 'Schema')
    def Schema(self, schema_id=None):
        """ Retrieve schema from parent object. The client class should
            override the method as Schema(self) and then call his method
            of the baseclass with the corresponding schema_id.
        """

        # Schema() seems to be called during the construction phase when there is
        # no acquisition context. So we return the default schema itself.

        if not hasattr(self, 'aq_parent'): 
            return self._wrap_schema(self.schema)

        # If we're called by the generated methods we can not rely on
        # the id and need to check for portal_type
        if not self.aq_parent.atse_isSchemaRegistered(self.portal_type):
            return self._wrap_schema(self.schema)

        if not schema_id:
            schema_id = self.portal_type
            
        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        self._v_schema = getattr(self, '_v_schema', None)
        if self._v_schema is None:

            # looking for changes in the schema hold by the object
            self._v_schema = self._lookupChanges(schema_id)
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

        return self._wrap_schema(self._v_schema)

    def _lookupChanges(self, atse_schema_id):
        """
        Checks if schema has changed
        """

        # looking if schema has changed
        atse_schema = self.aq_parent.atse_getSchemaById(atse_schema_id)
        object_schema = self.schema

        # XXX what about registered objects?
        if create_signature(atse_schema) != create_signature(object_schema):
            LOG('ATSchemaEditorNG', INFO, 'Schema %s changed on disk - refreshing' % atse_schema_id)
            self.aq_parent.atse_reRegisterSchema(atse_schema_id, object_schema)

        return self.aq_parent.atse_getSchemaById(atse_schema_id)

InitializeClass(ParentManagedSchema)
