"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: issue_schema.py,v 1.10 2003/09/21 12:55:02 ajung Exp $
"""

from OrderedSchema import OrderedSchema 
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IdWidget, StringWidget

VOCAB_TOPIC = DisplayList((
  ('UI', 'UI'),
  ('Backend', 'Backend'),
  ('Others', 'Others')
))

VOCAB_IMPORTANCE = DisplayList((
  ('low', 'Low'),
  ('medium', 'Medium'),
  ('high', 'High'),
  ('critical', 'Critical'),
))

VOCAB_SECURITY_RELATED = DisplayList((
  (0, 'No'),
  (1, 'Yes'),
))


schema = OrderedSchema((
    StringField('id',
                required=1,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                schemata='default',
                widget=IdWidget(label_msgid="label_name",
                                description_msgid="help_name",
                                i18n_domain="plone"),
                ),

    StringField('title',
                required=1,
                searchable=1,
                default='',
                accessor='Title',
                schemata='issuedata',
                widget=StringWidget(label_msgid="label_title",
                                    description_msgid="help_title",
                                    i18n_domain="plone"),
                ),
    StringField('description',
                required=1,
                searchable=1,
                schemata='issuedata',
                widget=TextAreaWidget,
                ),
    StringField('solution',
                searchable=1,
                schemata='issuedata',
                widget=TextAreaWidget(label='Solution',
                                      label_msgid='label_solution',
                                      i18n_domain='plonecollectorng'),
                ),
    StringField('topic',
                required=1,
                searchable=1,
                schemata='issuedata',
                vocabulary=VOCAB_TOPIC,
                widget=SelectionWidget(format='select',
                                       label='Topic',
                                       label_msgid='label_topic',
                                       i18n_domain='plonecollectorng'),
                ),
    StringField('importance',
                required=1,
                searchable=1,
                schemata='issuedata',
                vocabulary=VOCAB_IMPORTANCE,
                widget=SelectionWidget(format='select',
                                       label='Importance',
                                       label_msgid='label_importance',
                                       i18n_domain='plonecollectorng'),
                ),

    IntegerField('security_related',
                required=1,
                searchable=1,
                schemata='issuedata',
                vocabulary=VOCAB_SECURITY_RELATED,
                widget=SelectionWidget(format='select',
                                       label_msgid="label_security_related",
                                       label='Security related',
                                       i18n_domain="plone"),
                ),


    StringField('progress_hours_estimated',
                schemata='progress',
                widget=StringWidget(label='Hours estimated',
                                    label_msgid='label_hours_estimated',
                                    i18n_domain='plonecollectorng'),
                ),
    StringField('progress_hours_needed',
                schemata='progress',
                widget=StringWidget(label='Hours needed',
                                    label_msgid='label_hours_needed',
                                    i18n_domain='plonecollectorng'),
                ),
    StringField('progress_percent_done',
                schemata='progress',
                widget=StringWidget(label='Percent done',
                                    label_msgid='label_percent_done',
                                    i18n_domain='plonecollectorng'),
                ),
    # do not remove 'contact_name'
    StringField('contact_name',
                searchable=1,
                required=1,
                schemata='contact',
                widget=StringWidget(label='Name',
                                    label_msgid='label_contact_name',
                                    i18n_domain='plonecollectorng'),
                ),
    # do not remove 'contact_email'
    StringField('contact_email',
                searchable=1,
                required=1,
                schemata='contact',
                validators=('isEmail',),
                widget=StringWidget(label='E-Mail',
                                    label_msgid='label_contact_email',
                                    i18n_domain='plonecollectorng'),
                ),
    StringField('contact_address',
                searchable=1,
                schemata='contact',
                widget=StringWidget(label='Address',
                                    label_msgid='label_contact_address',
                                    i18n_domain='plonecollectorng'),
                ),
    StringField('contact_phone',
                searchable=1,
                schemata='contact',
                widget=StringWidget(label='Phone',
                                    label_msgid='label_contact_phone',
                                    i18n_domain='plonecollectorng'),
                ),
    StringField('contact_fax',
                searchable=1,
                schemata='contact',
                widget=StringWidget(label='Fax',
                                    label_msgid='label_contact_fax',
                                    i18n_domain='plonecollectorng'),
                ),
    ))
