"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: OrderedSchema.py,v 1.3 2003/09/18 19:25:59 ajung Exp $
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

InitializeClass(OrderedBaseFolder)
