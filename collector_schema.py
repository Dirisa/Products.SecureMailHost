"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: collector_schema.py,v 1.4 2003/09/07 17:51:01 ajung Exp $
"""

from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IntegerWidget
from Products.Archetypes.public import RichWidget

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


schema = BaseSchema +  Schema((
    StringField('description',
                searchable=1,
                ),
    IntegerField('limit_followups',
                vocabulary=VOC_LIMIT_FOLLOWUPS,
                widget=SelectionWidget(format='select'),
                default=0,
                ),

    StringField('canonical_hostname',
                default='http://localhost/',
                ),
    StringField('participation_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select'),
                default='staff'
                ),
    IntegerField('deadline_tickets',
                default=14,
                widget=IntegerWidget,
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
