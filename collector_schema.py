"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: collector_schema.py,v 1.5 2003/09/12 16:12:57 ajung Exp $
"""

from Products.Archetypes.public import Schema, DisplayList
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


schema = Schema((

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
                                    i18n_domain="plone"),
                ),

    StringField('description',
                searchable=1,
                schemata='collectordata',
                ),
    IntegerField('limit_followups',
                vocabulary=VOC_LIMIT_FOLLOWUPS,
                widget=SelectionWidget(format='select'),
                default=0,
                schemata='collectordata',
                ),

    StringField('canonical_hostname',
                default='http://localhost/',
                schemata='collectordata',
                ),
    StringField('participation_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select'),
                default='staff',
                schemata='collectordata',
                ),
    IntegerField('deadline_tickets',
                default=14,
                widget=IntegerWidget,
                schemata='collectordata',
                ),
    StringField('collector_email',
                searchable=0,
                default='root@localhost',
                schemata='E-Mail',
                ),
    StringField('email_notifications',
                vocabulary=VOC_EMAIL_NOTIFICATIONS,
                widget=SelectionWidget(format='select'),
                default='none',
                schemata='E-Mail'
                ),
    ))
