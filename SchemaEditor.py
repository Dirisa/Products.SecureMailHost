"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: SchemaEditor.py,v 1.11 2003/09/09 19:07:51 ajung Exp $
"""

import operator

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from BTrees.OOBTree import OOBTree
from Products.Archetypes.Schema import Schema
from Products.Archetypes.public import DisplayList
from Products.Archetypes.Field import *
from Products.Archetypes.Widget import *

import util
from config import ManageCollector

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    security = ClassSecurityInfo()

    security.declareProtected(ManageCollector, 'schema_init')
    def schema_init(self, schema):
        self._schema_names = []    # list of schemata names
        self._schemas = OOBTree()  # map schemata name to schemata

        for field in schema.fields():
            if not field.schemata in self._schema_names:
                self._schema_names.append(field.schemata)
                self._schemas[field.schemata] = Schema(field.schemata)
            self._schemas[field.schemata].addField(field)

    security.declareProtected(ManageCollector, 'getWholeSchema')
    def getWholeSchema(self):
        """ return the concatenation of all schemas """       
        l = [self._schemas[name] for name in self._schema_names]
        s = reduce(operator.__add__, l) 
        for field in s.fields():
            if field.mutator is None:
                field.mutator = 'archetypes_mutator'
            if field.edit_accessor is None:
                field.edit_accessor = 'archetypes_accessor'
            if field.accessor is None:
                field.accessor = 'archetypes_accessor'
        return s

    security.declareProtected(ManageCollector, 'getSchemaNames')
    def getSchemaNames(self):
        """ return names of all schematas """
        return self._schema_names

    security.declareProtected(ManageCollector, 'getSchema')
    def getSchema(self, name):
        """ return a schema given by its name """
        return self._schemas[name]

    security.declareProtected(ManageCollector, 'newSchema')
    def newSchema(self, fieldset, RESPONSE=None):
        """ add a new schema """
        if fieldset in self._schema_names:
            raise ValueError('Schemata "%s" already exists' % fieldset)
        self._schema_names.append(fieldset)
        self._schemas[fieldset] = Schema(fieldset)
        self._p_changed = 1

        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schema added', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'delSchema')
    def delSchema(self, fieldset, RESPONSE=None):
        """ delete a schema """
        self._schema_names.remove(fieldset)
        del self._schemas[fieldset]
        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schema deleted', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_del_field')
    def schema_del_field(self, fieldset, name, RESPONSE=None):
        """ remove a field from a fieldset """
        del self._schemas[fieldset][name]
        util.redirect(RESPONSE, 'pcng_schema_editor', 'Field deleted', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_update')
    def schema_update(self, REQUEST, RESPONSE=None):
        """ update a schema schema """

        R = REQUEST.form
        fieldset = R['fieldset'] 

        if R.has_key('schema_add_field'):
            fields = self._schemas[fieldset].fields()
            fields.append(StringField(R['name'], schemata=fieldset, widget=StringWidget))
            print fields
            schema = Schema(fieldset)
            for f in fields:
                schema.addField(f)
            self._schemas[fieldset] = schema

            util.redirect(RESPONSE, 'pcng_schema_editor', 'Field added', fieldset=fieldset)
            return            

        schema = Schema(fieldset)

        fieldnames = [name for name in R.keys()  if not isinstance(R[name], str) ]
        fieldnames.sort(lambda a,b,R=R: cmp(R[a].order, R[b].order))
        print fieldnames

        for name in fieldnames:
            print name
            d =  R[name]

            if d.field == 'StringField': field = StringField
            elif d.field == 'IntegerField': field = IntegerField
            elif d.field == 'FloatField': field = FloatField
            elif d.field == 'FixedPointField': field = FixedPointField
            elif d.field == 'BooleanField': field = BooleanField
            elif d.field == 'LinesField': field = LinesField
            elif d.field == 'DateTimeField': field = DateTimeField
            else: raise TypeError('unknown field type: %s' % d.field)

            D = {}
            D['default'] = d.get('default', '')
            D['schemata'] = fieldset
         
            if d.widget == 'String': pass
            elif d.widget == 'Select':      widget = SelectionWidget(format='select', visible=d.visible)
            elif d.widget == 'Radio':       widget = SelectionWidget(visible=d.visible)
            elif d.widget == 'Textarea':    widget = TextAreaWidget(visible=d.visible)
            elif d.widget == 'Calendar':    widget = CalendarWidget(visible=d.visible)
            elif d.widget == 'Boolean':     widget = BooleanWidget(visible=d.visible)
            elif d.widget == 'MultiSelect': widget = MultiSelectionWidget(visible=d.visible)
            elif d.widget == 'Keywords':    widget = KeywordWidget(visible=d.visible)
            elif d.widget == 'Richtext':    widget = RichWidget(visible=d.visible)
            elif d.widget == 'Password':    widget = PasswordWidget(visible=d.visible)
            elif d.widget == 'Visual':      widget = VisualWidget(visible=d.visible)
            else:
                raise ValueError('unknown widget type: %s' % d.widget)

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
            D['mutator'] = 'archetypes_mutator'
            D['accessor'] = 'archetypes_accessor'
            D['edit_accessor'] = 'archetypes_accessor'
            schema.addField(field(name, **D))

        self._schemas[fieldset] = schema

        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schema changed', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_get_fieldtype')
    def schema_get_fieldtype(self, field):
        """ return the type of a field """
        return field.__class__.__name__
    
    security.declareProtected(ManageCollector, 'schema_format_vocabulary')
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

