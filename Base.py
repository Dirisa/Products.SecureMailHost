"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Base.py,v 1.15 2004/09/11 12:45:21 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder
from Products.Archetypes.Schema import WrappedSchema

class ParentManagedSchema:
    """ mix-in class for AT content-types whose schema is managed by
        the parent container and retrieved through acquisition.
    """

    security = ClassSecurityInfo()    

    def Schemata(self):
        """ return dict of Schematas """
        d = {}
        schema = self.Schema()
        for name in schema.getSchemataNames():
            s = WrappedSchema()
            for f in schema.getSchemataFields(name):
                s.addField(f)
            d[name] = s.__of__(self)
        return d

    def Schema(self):
        """ Return our schema (through acquisition....uuuuuh). We override
            the Archetypes implementation because the schema for Issue is 
            maintained as attribute of the parent collector instance.
        """
        
        # Schema seems to be called during the construction phase when there is
        # not acquisition context. So we return the schema itself.

        if not hasattr(self, 'aq_parent'): return self.schema

        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        schema = getattr(self, '_v_schema', None)
        if schema is None:
            self._v_schema = self.aq_parent.atse_getSchema()

            for field in self._v_schema.fields():

                ##########################################################
                # Fake accessor and mutator methods
                ##########################################################

                name = field.getName()

                method = lambda self=self, name=name, *args, **kw: \
                         self.getField(name).get(self) 
                setattr(self, '_v_%s_accessor' % name, method )
                field.accessor = '_v_%s_accessor' % name
                field.edit_accessor = field.accessor

                method = lambda value,self=self, name=name, *args, **kw: \
                         self.getField(name).set(self, value) 
                setattr(self, '_v_%s_mutator' % name, method )
                field.mutator = '_v_%s_mutator' % name

                # Check if we need to update our own properties
                try:
                    value = field.get(self)  
                except:
                    field.set(self, field.default)
                        
        return self._v_schema.__of__(self)

InitializeClass(ParentManagedSchema)
