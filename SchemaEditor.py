"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: SchemaEditor.py,v 1.6 2003/09/07 11:16:25 ajung Exp $
"""

import operator

from BTrees.OOBTree import OOBTree
from Products.Archetypes.Schema import Schema
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, StringWidget

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    def test(self):
        """test"""
        self.schema_init()
        print 'done'

    def schema_init(self, schema):
        self._schema_names = []    # list of schemata names
        self._schemas = OOBTree()  # map schemata name to schemata

        for field in schema.fields():
            if not field.schemata in self._schema_names:
                self._schema_names.append(field.schemata)
                self._schemas[field.schemata] = Schema(field.schemata)
            self._schemas[field.schemata].addField(field)

    def getWholeSchema(self):
        """ return the concatenation of all schemas """       
        l = [self._schemas[name] for name in self._schema_names]
        return reduce(operator.__add__, l) 

    def getSchemaNames(self):
        """ return names of all schematas """
        return self._schema_names

    def getSchema(self, name):
        """ return a schema given by its name """
        print name, self._schemas[name]
        return self._schemas[name]

    def newSchema(self, name, RESPONSE=None):
        """ add a new schema """
        if name in self._schema_names:
            raise ValueError('Schemata "%s" already exists' % name)
        self._schema_names.append(name)
        self._schemas[name] = Schema(name)
        self._p_changed = 1

        if RESPONSE is not None:
            RESPONSE.redirect('pcng_schema_editor?fieldset=%s&portal_status_message=Schema%%20added' % name)

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


        if R.has_key('schema_add_field'):
            schema = self._schemas[fieldset]
            print schema
            print schema.fields()
            field = StringField(R['name'], schemata=fieldset, widget=StringWidget)
            schema.addField(field)
            self._p_changed = 1
            schema._p_changed = 1
            self._schemas._p_changed = 1
            print "-->",self._schemas[fieldset]
            print "-->",self._schemas[fieldset].fields()

            if RESPONSE is not None:
                RESPONSE.redirect('pcng_schema_editor?fieldset=%s&portal_status_message=Field added' % fieldset)
            return            

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

            if d.widget in ('Radio', 'Select'):

                vocab = d.get('vocabulary', [])
                l = []
                for line in vocab:
                    line = line.strip()
                    if line.find('|') == -1:
                        k = v = line
                    else:
                        k,v = line.split('|', 1)
                    l.append( (k,v))

                D['vocabulary'] = DisplayList(l)

            D['required'] = d.get('required', 0)
            schema.addField(field(name, **D))

        print schema
        self._schemas[fieldset] = schema

        if RESPONSE is not None:
            RESPONSE.redirect('pcng_schema_editor?fieldset=%s&portal_status_message=Schema changed' % fieldset)

    def schema_get_fieldtype(self, field):
        """ return the type of a field """
        return field.__class__.__name__
    
    def schema_format_vocabulary(self, field):
        """ format the DisplayList of a field to be display
            within a textarea.
        """
        l = []
        for k in field.vocabulary:
            v = field.vocabulary.getValue(k)
            if k == v: l.append(k)
            else: l.append('%s|%s' % (k,v))
        return '\n'.join(l)
