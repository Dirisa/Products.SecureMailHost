"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: collector_schema.py,v 1.9 2003/09/28 14:06:25 ajung Exp $
"""

from OrderedSchema import OrderedSchema
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IntegerWidget
from Products.Archetypes.public import RichWidget, IdWidget, StringWidget

VOC_LIMIT_FOLLOWUPS = DisplayList((
  (1, 'Yes'),
  (0, 'No'),                                       
))

VOC_PARTICIPATION_MODE = DisplayList((
  ('staff', 'Only staff members'),
  ('authenticated', 'Any authenticated user'),                                       
  ('anyone', 'Anyone'),                                       
))

VOC_EMAIL_NOTIFICATIONS = DisplayList((
  ('all', 'Trackeradmins + Supporters + Reporters'),
  ('assigned', 'Trackeradmins + assigned Supporters + Reporters'),                                       
  ('none', 'no notifications'),                                       
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
                schemata='collectordata',
                widget=StringWidget(label_msgid="label_title",
                                    description_msgid="help_title",
                                    label='Title',
                                    i18n_domain="plone"),
                ),

    StringField('description',
                searchable=1,
                schemata='collectordata',
                widget=TextAreaWidget(label='Description'),
                ),
    IntegerField('limit_followups',
                vocabulary=VOC_LIMIT_FOLLOWUPS,
                widget=SelectionWidget(format='select',
                                       label='Limit followups'),
                default=0,
                schemata='collectordata',
                ),

    StringField('canonical_hostname',
                default='http://localhost/',
                widget=StringWidget(label='Canonical hostname'),
                schemata='collectordata',
                ),
    StringField('participation_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select', 
                                       label='Participation mode'),
                default='staff',
                schemata='collectordata',
                ),
    StringField('view_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select', 
                                       label='View mode'),
                default='staff',
                schemata='collectordata',
                ),
    IntegerField('deadline_tickets',
                default=14,
                widget=StringWidget(label='Deadline for new tickets'),
                schemata='collectordata',
                ),
    StringField('collector_email',
                searchable=0,
                default='root@localhost',
                widget=StringWidget(label='E-Mail address (FROM: header)'),
                schemata='E-Mail',
                ),
    StringField('email_notifications',
                vocabulary=VOC_EMAIL_NOTIFICATIONS,
                widget=SelectionWidget(format='select', label='E-Mail notifications'),
                default='none',
                schemata='E-Mail'
                ),
    ))
