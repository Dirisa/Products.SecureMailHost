"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: SchemaEditor.py,v 1.3 2003/09/07 07:58:24 ajung Exp $
"""

import operator

from BTrees.OOBTree import OOBTree
from Products.Archetypes.Schema import Schema
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget

import issue_schema 

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    def test(self):
        """test"""
        self.schema_init()
        print 'done'

    def getWholeSchema(self):
        """ return the concatenation of all schemas """       
        l = [self._schemas[name] for name in self._schema_names]
        return reduce(operator.__add__, l) 

    def schema_init(self):

        self._schema_names = []    # list of schemata names
        self._schemas = OOBTree()  # map schemata name to schemata

        for field in issue_schema.schema.fields():
            if not field.schemata in self._schema_names:
                self._schema_names.append(field.schemata)
                self._schemas[field.schemata] = Schema(field.schemata)
            self._schemas[field.schemata].addField(field)

    def getSchemaNames(self):
        """ return names of all schematas """
        return self._schema_names

    def getSchema(self, name):
        """ return a schema given by its name """
        return self._schemas[name]

    def newSchema(self, name, RESPONSE=None):
        """ add a new schema """
        self._schema_names.append(name)
        self._schemas[name] = None
        self._p_changed = 1

        if RESPONSE is not None:
            RESPONSE.redirect('pcng_schema_editor?portal_status_message=Schema%20added')

    def delSchema(self, name, RESPONSE=None):
        """ delete a schema """
        self._schema_names.remove(name)
        del self._schemas[name]
        if RESPONSE is not None:
            RESPONSE.redirect('pcng_schema_editor?portal_status_message=Schema%20deleted')

    def schema_update(self, REQUEST, RESPONSE=None):
        """ update a schema schema """

        R = REQUEST.form
        fieldset = R['fieldset'] 

        schema = Schema(fieldset)
        fieldnames = [name for name in R.keys()  if not isinstance(R[name], str) ]
        fieldnames.sort(lambda a,b,R=R: cmp(R[a].order, R[b].order))

        for name in fieldnames:
            d =  R[name]

            if d.field == 'StringField': field = StringField
            elif d.field == 'IntegerField': field = IntegerField
            else: raise TypeError('unknown field type: %s' % d.field)

            print d
            D = {}
            D['default'] = d.get('default', '')
            D['schemata'] = fieldset
            if d.widget == 'String': pass
            elif d.widget == 'Select': D['widget'] = SelectionWidget(format='select')
            elif d.widget == 'Radio': D['widget'] = SelectionWidget
            elif d.widget == 'Textarea': D['widget'] = TextAreaWidget

            D['required'] = d.get('required', 0)
            schema.addField(field(name, **D))


        self._schemas[fieldset] = schema

        if RESPONSE is not None:
            RESPONSE.redirect('pcng_schema_editor?fieldset=%s&portal_status_message=Schema changed' % fieldset)

