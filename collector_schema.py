from Products.Archetypes.public import BaseSchema, Schema, DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget
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
                widget=SelectionWidget,
                default=0,
                ),
    StringField('email_notifications',
                vocabulary=VOC_EMAIL_NOTIFICATIONS,
                widget=SelectionWidget,
                default='none',
                ),
    StringField('canonical_hostname',
                default='http://localhost/',
                ),
    StringField('participation_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget,
                default='staff'
                ),
    IntegerField('deadline_tickets',
                default=14,
                ),
    StringField('collector_email',
                searchable=0,
                default='root@localhost',
                ),
    ))
