"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: OrderedSchema.py,v 1.6 2003/11/01 17:03:26 ajung Exp $
"""

from Globals import InitializeClass
from Products.Archetypes.public import Schema, BaseFolder
from Products.Archetypes.utils import OrderedDict

class OrderedSchema(Schema):
    """ Provide basic order support for Archetypes schemas """

    def __init__(self, *args, **kwargs):
        self._ordered_keys = []   # ordered list of field names
        Schema.__init__(self, *args, **kwargs)

    def addField(self, field):
        """ add a field and keep track of ordered keys """
        Schema.addField(self, field)
        if not hasattr(self, '_ordered_keys'):
            self._ordered_keys = []   # ordered list of field names

        self._ordered_keys.append(field.getName())
        self._p_changed = 1

    def fields(self):
        """ fields wrapper """

        fields = Schema.fields(self)
        fields.sort(lambda x,y,k=self._ordered_keys: cmp(k.index(x.getName()), k.index(y.getName())))
        return fields

    def __add__(self, other):
        c = OrderedSchema()
        #We can't use update and keep the order so we do it manually
        for field in self.fields():
            c.addField(field)
        for field in other.fields():
            c.addField(field)

        #XXX This should also merge properties (last write wins)
        c._layers = self._layers.copy()
        c._layers.update(other._layers)
        return c

    def copy(self):
        c = OrderedSchema()
        for field in self.fields():
            c.addField(field.copy())
        return c

InitializeClass(OrderedSchema)


class OrderedBaseFolder(BaseFolder):
    """ Base class for a folder using an OrderedSchema """

    def getSchemaNames(self):
        """ return ordered list of schema names """
        lst = []
        for k in self.schema._ordered_keys:
            field = self.Schema()[k]
            if not field.schemata in lst:
                if not field in ('default', 'metadata'):
                    lst.append(field.schemata)
        return lst

    def base_edit(self, RESPONSE):
        """ blabla """
        RESPONSE.redirect('pcng_base_edit')
    

InitializeClass(OrderedBaseFolder)
