"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: collector_schema.py,v 1.40 2004/04/18 11:36:44 ajung Exp $
"""


from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField, DateTimeField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IntegerWidget
from Products.Archetypes.public import RichWidget, IdWidget, StringWidget

from PCNGSchema import PCNGSchema as Schema
from notification_policies import VOC_NOTIFICATION_POLICIES
from workflows import VOC_WORKFLOWS

VOC_NOTIFICATION_LANGUAGES = DisplayList((
  ('en', 'English'),
  ('de', 'German'),
  ('fi', 'Finish'),
  ('nl', 'Dutch'),
  ('pt-br', 'Portuguese/Brazil'),
))

VOC_PARTICIPATION_MODE = DisplayList((
  ('staff', 'Only staff members'),
  ('authenticated', 'Any authenticated user'),                                       
  ('anyone', 'Anyone'),                                       
))

VOC_ISSUE_EMAIL_SUBMISSION = DisplayList((
  ('disabled', 'Disabled'),
  ('staff', 'Only staff members'),
  ('authenticated', 'Any authenticated user'),                                       
  ('anyone', 'Anyone'),                                       
))

VOC_ISSUE_EMAIL_VERIFICATION = DisplayList((
  ('disabled', 'Disabled'),
  ('enabled', 'Enabled'),
  ('paranoid', 'Paranoid mode (reserved for later mode)'),
))


VOC_WATCHLIST = DisplayList((
  ('disabled', 'Disabled'),
  ('anonymous', 'Watchlist enabled for anyone'),
  ('authenticated', 'Watchlist enabled for authenticated users'),
))

VOC_SLOTS_MODE= DisplayList((
  ('plone', 'Use Plone settings'),
  ('left', 'Keep left Plone slot, clear right'),
  ('right', 'Clear left Plone slot, keep right'),
  ('clear', 'Clear all Plone slots'),
))

VOC_NAVIGATION_SLOT = DisplayList((
  ('yes', 'Yes'),
  ('no', 'No'),                                       
))


schema = Schema((

    StringField('id',
                required=1,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                schemata='collectordata',
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

    DateTimeField('effectiveDate', schemata='default'),
    DateTimeField('expirationDate', schemata='default'),

    StringField('description',
                required=1,
                searchable=1,
                schemata='collectordata',
                widget=TextAreaWidget(label='Description',
                                      label_msgid='label_description',
                                      i18n_domain='plonecollectorng'),
                ),

    StringField('canonical_hostname',
                default='localhost',
                widget=StringWidget(label='Hostname or IP address (used as part of the URL inside email notifications)',
                                     label_msgid='label_hostname',
                                     i18n_domain='plonecollectorng'),
                schemata='E-Mail',
                ),
    StringField('participation_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select', 
                                       label='Participation mode (who can file issues)',
                                       label_msgid='label_participation_mode',
                                       i18n_domain='plonecollectorng'),
                default='staff',
                schemata='collectordata',
                ),
    StringField('view_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select', 
                                       label='View mode (who can view issues)',
                                       label_msgid='label_view_mode',
                                       i18n_domain='plonecollectorng'),
                default='staff',
                schemata='collectordata',
                ),
    IntegerField('deadline_tickets',
                default=14,
                widget=StringWidget(label='Automatic deadline in days for new issues',
                                    label_msgid='label_deadline_tickets',
                                    i18n_domain='plonecollectorng'),
                schemata='collectordata',
                ),
    StringField('collector_workflow',
                vocabulary=VOC_WORKFLOWS,
                default='pcng_issue_workflow (PloneCollectorNG default workflow)',
                widget=SelectionWidget(format='select', 
                                       label='Workflow',
                                       label_msgid='label_workflow',
                                       i18n_domain='plonecollectorng'),
                schemata='collectordata'
                ),
    StringField('collector_email',
                searchable=0,
                default='plonecollectorng@somedomain.com',
                widget=StringWidget(label='E-Mail address (FROM: + REPLY-TO: header)',
                                    label_msgid='label_email_address',
                                    i18n_domain='plonecollectorng'),
                schemata='E-Mail',
                ),
    StringField('collector_abbreviation',
                searchable=0,
                default='',
                widget=StringWidget(label='Abbreviation (used in the email subject to identify the collector)',
                                    label_msgid='label_collector_abbreviation',
                                    i18n_domain='plonecollectorng'),
                schemata='E-Mail',
                ),
    StringField('issue_email_submission',
                default='disabled',
                vocabulary=VOC_ISSUE_EMAIL_SUBMISSION(),
                widget=SelectionWidget(format='select',
                                    label='Issue submissions through email)',
                                    label_msgid='label_issue_email_submission',
                                    i18n_domain='plonecollectorng'),
                schemata='E-Mail',
                ),
    StringField('issue_email_verification',
                default='disabled',
                vocabulary=VOC_ISSUE_EMAIL_VERIFICATION(),
                widget=SelectionWidget(format='select',
                                    label='Verify incoming issue email submissions',
                                    label_msgid='label_issue_email_verification',
                                    i18n_domain='plonecollectorng'),
                schemata='E-Mail',
                ),
    StringField('notification_policy',
                vocabulary=VOC_NOTIFICATION_POLICIES(),
                widget=SelectionWidget(format='select', label='E-Mail notification policy',
                                       label_msgid='label_email_notification_policy',
                                       i18n_domain='plonecollectorng'),
                default='NoneNotificationPolicy',
                schemata='E-Mail'
                ),
    StringField('notification_language',
                vocabulary=VOC_NOTIFICATION_LANGUAGES,
                default='en',
                widget=SelectionWidget(format='select', 
                                       label='Notification language',
                                       label_msgid='label_notification_language',
                                       i18n_domain='plonecollectorng'),
                schemata='E-Mail'
                ),

    StringField('watchlist_mode',
                vocabulary=VOC_WATCHLIST,
                widget=SelectionWidget(format='select', 
                                       label='Watchlist (Subscription to an issue)',
                                       label_msgid='label_watchlist',
                                       i18n_domain='plonecollectorng'),
                default='disabled',
                schemata='collectordata'
                ),

    StringField('slots_mode',
                vocabulary=VOC_SLOTS_MODE,
                widget=SelectionWidget(format='select', 
                                       label='Plone slots',
                                       label_msgid='label_slots_mode',
                                       i18n_domain='plonecollectorng'),
                default='plone',
                schemata='Look and Feel'
                ),
    StringField('navigation_slot',
                vocabulary=VOC_NAVIGATION_SLOT,
                widget=SelectionWidget(format='select', 
                                       label='Navigation slot',
                                       label_msgid='label_navigation_slot',
                                       i18n_domain='plonecollectorng'),
                default='no',
                schemata='Look and Feel'
                ),
    ))
