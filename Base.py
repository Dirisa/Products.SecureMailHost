"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Base.py,v 1.9 2003/12/13 11:32:10 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder
from Products.Archetypes.Schema import Schema

class Base(BaseBTreeFolder):
    """ base class for collector/issues """

    def SchemataNames(self):
        """ return ordered list of schemata names """
        return [n for n in self.Schema().getSchemataNames() if not n in ('default', 'metadata')]

    def base_edit(self, RESPONSE):
        """ redirect to our own edit method """
        RESPONSE.redirect('pcng_base_edit')

InitializeClass(Base)


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
            s = Schema()
            for f in schema.getSchemataFields(name):
                s.addField(f)
            d[name] = s
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
                         self.Schema()[name].storage.get(name, self) 
                setattr(self, '_v_%s_accessor' % name, method )
                field.accessor = '_v_%s_accessor' % name
                field.edit_accessor = field.accessor

                method = lambda value,self=self, name=name, *args, **kw: \
                         self.Schema()[name].storage.set(name, self, value) 
                setattr(self, '_v_%s_mutator' % name, method )
                field.mutator = '_v_%s_mutator' % name

                # Check if we need to update our own properties
                try:
                    value = field.storage.get(field.getName(), self)  
                except:
                    field.storage.set(field.getName(), self, field.default)
                        
        return self._v_schema

InitializeClass(ParentManagedSchema)
