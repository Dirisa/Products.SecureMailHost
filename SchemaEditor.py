"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: SchemaEditor.py,v 1.14 2003/09/14 14:42:48 ajung Exp $
"""

import operator

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from BTrees.OOBTree import OOBTree
from Products.Archetypes.public import DisplayList
from Products.Archetypes.Field import *
from Products.Archetypes.Widget import *

import util
from config import ManageCollector
from OrderedSchema import OrderedSchema

class SchemaEditor:
    """ a simple TTW editor for Archetypes schemas """

    security = ClassSecurityInfo()

    security.declareProtected(ManageCollector, 'schema_init')
    def schema_init(self, schema):
        self._schemata_names = []    # list of schemata names
        self._schemas = OOBTree()  # map schemata name to schemata

        for field in schema.fields():
            if not field.schemata in self._schemata_names:
                self._schemata_names.append(field.schemata)
                self._schemas[field.schemata] = OrderedSchema()
            self._schemas[field.schemata].addField(field)

    security.declareProtected(ManageCollector, 'schema_getWholeSchema')
    def schema_getWholeSchema(self):
        """ return the concatenation of all schemas """       
        l = [self._schemas[name] for name in self._schemata_names]
        s = reduce(operator.__add__, l) 
        for field in s.fields():
            if field.mutator is None:
                field.mutator = 'archetypes_mutator'
            if field.edit_accessor is None:
                field.edit_accessor = 'archetypes_accessor'
            if field.accessor is None:
                field.accessor = 'archetypes_accessor'
        return s

    security.declareProtected(ManageCollector, 'schema_getNames')
    def schema_getNames(self):
        """ return names of all schematas """
        return self._schemata_names

    security.declareProtected(ManageCollector, 'schema_getSchema')
    def schema_getSchema(self, name):
        """ return a schema given by its name """
        return self._schemas[name]

    security.declareProtected(ManageCollector, 'schema_newSchema')
    def schema_newSchema(self, fieldset, RESPONSE=None):
        """ add a new schema """
        if fieldset in self._schemata_names:
            raise ValueError('Schemata "%s" already exists' % fieldset)
        self._schemata_names.append(fieldset)
        self._schemas[fieldset] = OrderedSchema()
        self._p_changed = 1

        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schema added', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_delSchema')
    def schema_delSchema(self, fieldset, RESPONSE=None):
        """ delete a schema """
        self._schemata_names.remove(fieldset)
        del self._schemas[fieldset]
        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schema deleted', fieldset=self._schemata_names[0])

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
            schema = OrderedSchema()
            for f in fields:
                schema.addField(f)
            self._schemas[fieldset] = schema

            util.redirect(RESPONSE, 'pcng_schema_editor', 'Field added', fieldset=fieldset)
            return            

        schema = OrderedSchema()
        fieldnames = [name for name in R.keys()  if not isinstance(R[name], str) ]
        fieldnames.sort(lambda a,b,R=R: cmp(R[a].order, R[b].order))

        for name in fieldnames:
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
         
            visible = d.get('visible', 1)
            if d.widget == 'String':        widget = StringWidget(visible=visible)
            elif d.widget == 'Select':      widget = SelectionWidget(format='select', visible=visible)
            elif d.widget == 'Radio':       widget = SelectionWidget(visible=visible)
            elif d.widget == 'Textarea':    widget = TextAreaWidget(visible=visible)
            elif d.widget == 'Calendar':    widget = CalendarWidget(visible=visible)
            elif d.widget == 'Boolean':     widget = BooleanWidget(visible=visible)
            elif d.widget == 'MultiSelect': widget = MultiSelectionWidget(visible=visible)
            elif d.widget == 'Keywords':    widget = KeywordWidget(visible=visible)
            elif d.widget == 'Richtext':    widget = RichWidget(visible=visible)
            elif d.widget == 'Password':    widget = PasswordWidget(visible=visible)
            elif d.widget == 'Lines':       widget = LinesWidget(visible=visible)
            elif d.widget == 'Visual':      widget = VisualWidget(visible=visible)
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
            D['widget'] = widget
            D['mutator'] = 'archetypes_mutator'
            D['accessor'] = 'archetypes_accessor'
            D['edit_accessor'] = 'archetypes_accessor'

            schema.addField(field(name, **D))

        self._schemas[fieldset] = schema

        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schema changed', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_moveLeft')
    def schema_moveLeft(self, fieldset, RESPONSE=None):
        """ move a schemata to the left"""
        pos = self._schemata_names.index(fieldset)
        if pos > 0:
            self._schemata_names.remove(fieldset)
            self._schemata_names.insert(pos-1, fieldset)
        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schemata moved to left', fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_moveRight')
    def schema_moveRight(self, fieldset, RESPONSE=None):
        """ move a schemata to the right"""
        pos = self._schemata_names.index(fieldset)
        if pos < len(self._schemata_names):
            self._schemata_names.remove(fieldset)
            self._schemata_names.insert(pos+1, fieldset)
        util.redirect(RESPONSE, 'pcng_schema_editor', 'Schemata moved to right ', fieldset=fieldset)

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

InitializeClass(SchemaEditor)
