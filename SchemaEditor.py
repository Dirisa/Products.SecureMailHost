"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: SchemaEditor.py,v 1.29 2003/11/11 08:02:16 ajung Exp $
"""

import operator
from types import StringType

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import *
from BTrees.OOBTree import OOBTree
from Products.Archetypes.public import DisplayList
from Products.Archetypes.Field import *
from Products.Archetypes.Widget import *

import util
from config import ManageCollector
from OrderedSchema import OrderedSchema

UNDELETEABLE_FIELDS = ('title', 'description', 'classification', 'topic', 'importance', 'contact_email', 'contact_name')


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

    security.declareProtected(View, 'schema_getWholeSchema')
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

    security.declareProtected(View, 'schema_getNames')
    def schema_getNames(self):
        """ return names of all schematas """
        return self._schemata_names

    security.declareProtected(View, 'schema_getSchema')
    def schema_getSchema(self, name):
        """ return a schema given by its name """
        return self._schemas[name]

    security.declareProtected(ManageCollector, 'schema_newSchema')
    def schema_newSchema(self, fieldset, RESPONSE=None):
        """ add a new schema """
        if not fieldset:
            raise TypeError(self.translate('schema_empty_name', 'Empty ID given'))

        if fieldset in self._schemata_names:
            raise ValueError(self.translate('schema_exists', 'Schemata "$schema" already exists', schema=fieldset))
        self._schemata_names.append(fieldset)
        self._schemas[fieldset] = OrderedSchema()
        self._p_changed = 1

        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_added', 'Schema added'), fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_delSchema')
    def schema_delSchema(self, fieldset, RESPONSE=None):
        """ delete a schema """
        self._schemata_names.remove(fieldset)
        del self._schemas[fieldset]
        self._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_deleted', 'Schema deleted'), fieldset=self._schemata_names[0])

    security.declareProtected(ManageCollector, 'schema_del_field')
    def schema_del_field(self, fieldset, name, RESPONSE=None):
        """ remove a field from a fieldset """

        if name in UNDELETEABLE_FIELDS:
            raise ValueError(self.translate('schema_feld_not_deleteable','field "$name" can not be deleted', name=name))
            
        del self._schemas[fieldset][name]
        self._schemas._p_changed = 1
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_field_deleted', 'Field deleted'), fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_update')
    def schema_update(self, fielddata,  REQUEST, RESPONSE=None):
        """ update a single field"""

        R = REQUEST.form
        FD = fielddata

        ## ATT: this should go into a dedicated method
        if R.has_key('schema_add_field'):
            if not R['name']:
                raise ValueError(self.translate('schema_empty_field_name', 'Field name is empty'))
        
            fieldset = FD.schemata    
            fields = self._schemas[fieldset].fields()
            fields.append(StringField(R['name'], schemata=fieldset, widget=StringWidget))
            schema = OrderedSchema()
            for f in fields:
                schema.addField(f)
            self._schemas[fieldset] = schema

            util.redirect(RESPONSE, 'pcng_schema_editor', 
                          self.translate('schema_field_added', 'Field added'), fieldset=fieldset, field=R['name'])
            return            

        if   FD.type == 'StringField':     field = StringField
        elif FD.type == 'IntegerField':    field = IntegerField
        elif FD.type == 'FloatField':      field = FloatField
        elif FD.type == 'FixedPointField': field = FixedPointField
        elif FD.type == 'BooleanField':    field = BooleanField
        elif FD.type == 'LinesField':      field = LinesField
        elif FD.type == 'DateTimeField':   field = DateTimeField
        else: raise TypeError(self.translate('schema_unknown_field', 'unknown field type: $field', field=FD.field))

        D = {}    # dict to be passed to the field constructor
        D['default'] = FD.get('default', '')
        D['schemata'] = FD.schemata
         
        if FD.get('invisible', 0) == 0:
            visible = 1
        else:
            visible = 0

        # build widget
        if   FD.widget == 'String':      widget = StringWidget()
        elif FD.widget == 'Select':      widget = SelectionWidget(format='select')
        elif FD.widget == 'Flex':        widget = SelectionWidget(format='flex')
        elif FD.widget == 'Radio':       widget = SelectionWidget(format='radio')
        elif FD.widget == 'Textarea':    widget = TextAreaWidget()
        elif FD.widget == 'Calendar':    widget = CalendarWidget()
        elif FD.widget == 'Boolean':     widget = BooleanWidget()
        elif FD.widget == 'MultiSelect': widget = MultiSelectionWidget()
        elif FD.widget == 'Keywords':    widget = KeywordWidget()
        elif FD.widget == 'Richtext':    widget = RichWidget()
        elif FD.widget == 'Password':    widget = PasswordWidget()
        elif FD.widget == 'Lines':       widget = LinesWidget()
        elif FD.widget == 'Visual':      widget = VisualWidget()
        else: raise ValueError(self.translate('schema_unknown_widget', 'unknown widget type: $widget', widget=d.widget))

        if hasattr(widget, 'size'):
            widget.size = FD.widgetsize
        elif hasattr(widget, 'rows'):
            if FD.widgetsize.find('x') == -1:
                rows = FD.widgetsize
                cols = 80
            else:
                rows, cols = FD.widgetsize.split('x')
                widget.rows = int(rows)
                widget.cols = int(cols)

        widget.visible = visible
        widget.label = FD.label
        widget.label_msgid = 'label_' + FD.label
        widget.i18n_domain = 'plonecollectorng'

        D['widget'] = widget

        # build DisplayList instance for SelectionWidgets
        if FD.widget in ('Radio', 'Select', 'MultiSelect'):
            vocab = FD.get('vocabulary', [])

            # The vocabulary can either be a list of string of 'values'
            # or a list of strings 'key|value' or a list with *one*
            # string 'method:<methodname>'. 'method:<methodname>' is used
            # specify a method that is called to retrieve a DisplayList
            # instance

            if len(vocab) == 1 and vocab[0].startswith('method:'):
                dummy,method = vocab[0].split(':')
                D['vocabulary'] = method.strip()
            else:
                l = []
                for line in vocab:
                    line = line.strip()
                    if not line: continue
                    if line.find('|') == -1:
                        k = v = line
                    else:
                        k,v = line.split('|', 1)
                    l.append( (k,v))

                D['vocabulary'] = DisplayList(l)

        D['required'] = FD.get('required', 0)
        D['mutator'] = 'archetypes_mutator'
        D['accessor'] = 'archetypes_accessor'
        D['edit_accessor'] = 'archetypes_accessor'

        field = field(FD.name, **D)

        # build new schemata
        schema = self._schemas[FD.schemata]
        new_schema = OrderedSchema()
        for f in schema.fields():
            if f.getName() == FD.name:
                new_schema.addField(field)
            else:
                new_schema.addField(f)

        self._schemas[FD.schemata] = new_schema # and replace old one
        
        util.redirect(RESPONSE, 'pcng_schema_editor', 'Field changed', 
                      fieldset=FD.schemata, field=FD.name)

    security.declareProtected(ManageCollector, 'schema_moveLeft')
    def schema_moveLeft(self, fieldset, RESPONSE=None):
        """ move a schemata to the left"""
        pos = self._schemata_names.index(fieldset)
        if pos > 0:
            self._schemata_names.remove(fieldset)
            self._schemata_names.insert(pos-1, fieldset)
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_moved_left', 'Schemata moved to left'), fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_moveRight')
    def schema_moveRight(self, fieldset, RESPONSE=None):
        """ move a schemata to the right"""
        pos = self._schemata_names.index(fieldset)
        if pos < len(self._schemata_names):
            self._schemata_names.remove(fieldset)
            self._schemata_names.insert(pos+1, fieldset)
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_moved_right', 'Schemata moved to right'), fieldset=fieldset)

    security.declareProtected(ManageCollector, 'schema_field_up')
    def schema_field_up(self, fieldset, name, RESPONSE=None):
        """ move a field of schemata up """

        fields = self._schemas[fieldset].fields()
        for i in range(len(fields)):
            field = fields[i]
            if field.getName() == name and i>0:
                del fields[i]
                fields.insert(i-1,field)
                break

        schema = OrderedSchema()
        for field in fields:
            schema.addField(field)

        self._schemas[fieldset] = schema
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_field_moved_up', 'Field moved up'), fieldset=fieldset, field=name)

    security.declareProtected(ManageCollector, 'schema_field_down')
    def schema_field_down(self, fieldset, name, RESPONSE=None):
        """ move a field of schemata down """

        fields = self._schemas[fieldset].fields()
        for i in range(len(fields)):
            field = fields[i]
            if field.getName() == name and i < len(fields):
                del fields[i]
                fields.insert(i+1,field)
                break

        schema = OrderedSchema()
        for field in fields:
            schema.addField(field)

        self._schemas[fieldset] = schema
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_field_moved_down', 'Field moved down'), fieldset=fieldset, field=name)

    security.declareProtected(ManageCollector, 'schema_field_to_fieldset')
    def schema_field_to_fieldset(self, fieldset, name, RESPONSE=None):
        """ move a field from the current fieldset to another one """

        field = self.schema_getWholeSchema()[name]
        del self._schemas[field.schemata][name]
        self._schemas[fieldset].addField(field)
        util.redirect(RESPONSE, 'pcng_schema_editor', 
                      self.translate('schema_field_moved', 'Field moved to other fieldset'), fieldset=fieldset, field=name)

    security.declareProtected(ManageCollector, 'schema_get_fieldtype')
    def schema_get_fieldtype(self, field):
        """ return the type of a field """
        return field.__class__.__name__
    
    security.declareProtected(ManageCollector, 'schema_format_vocabulary')
    def schema_format_vocabulary(self, field):
        """ format the DisplayList of a field to be display
            within a textarea.
        """

        if isinstance(field.vocabulary, StringType):
            return 'method:' + field.vocabulary

        l = []
        for k in field.vocabulary:
            v = field.vocabulary.getValue(k)
            if k == v: l.append(k)
            else: l.append('%s|%s' % (k,v))
        return '\n'.join(l)

InitializeClass(SchemaEditor)
