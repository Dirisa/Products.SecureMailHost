"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: collector_schema.py,v 1.22 2003/11/28 07:32:33 ajung Exp $
"""

from OrderedSchema import OrderedSchema
from Products.Archetypes.public import DisplayList
from Products.Archetypes.public import StringField, TextField, IntegerField, DateTimeField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IntegerWidget
from Products.Archetypes.public import RichWidget, IdWidget, StringWidget

from config import VOC_ISSUE_FORMATTERS
from notification_policies import VOC_NOTIFICATION_POLICIES

VOC_LIMIT_FOLLOWUPS = DisplayList((
  (1, 'Yes'),
  (0, 'No'),                                       
))

VOC_PARTICIPATION_MODE = DisplayList((
  ('staff', 'Only staff members'),
  ('authenticated', 'Any authenticated user'),                                       
  ('anyone', 'Anyone'),                                       
))

VOC_WATCHLIST = DisplayList((
  ('disabled', 'Disabled'),
  ('anonymous', 'Watchlist enabled for anyone'),
  ('authenticated', 'Watchlist enabled for authenticated users'),
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

    DateTimeField('effectiveDate', schemata='metadata'),
    DateTimeField('expirationDate', schemata='metadata'),

    StringField('description',
                required=1,
                searchable=1,
                schemata='collectordata',
                widget=TextAreaWidget(label='Description',
                                       label_msgid='label_description',
                                       i18n_domain='plonecollectorng'),
                ),
    IntegerField('limit_followups',
                vocabulary=VOC_LIMIT_FOLLOWUPS,
                widget=SelectionWidget(format='select',
                                       label='Limit followups',
                                       label_msgid='label_limit_followups',
                                       i18n_domain='plonecollectorng'),
                default=0,
                schemata='collectordata',
                ),

    StringField('canonical_hostname',
                default='localhost',
                widget=StringWidget(label='Hostname or IP address',
                                       label_msgid='label_hostname',
                                       i18n_domain='plonecollectorng'),
                schemata='collectordata',
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
    StringField('collector_email',
                searchable=0,
                default='root@localhost',
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
    StringField('notification_policy',
                vocabulary=VOC_NOTIFICATION_POLICIES(),
                widget=SelectionWidget(format='select', label='E-Mail notification policy',
                                       label_msgid='label_email_notification_policy',
                                       i18n_domain='plonecollectorng'),
                default='NoneNotificationPolicy',
                schemata='E-Mail'
                ),
    StringField('issue_formatter',
                vocabulary=VOC_ISSUE_FORMATTERS,
                widget=SelectionWidget(format='select', label='E-Mail issue formatter',
                                       label_msgid='label_email_issue_formatters',
                                       i18n_domain='plonecollectorng'),
                schemata='E-Mail'
                ),
    StringField('watchlist_mode',
                vocabulary=VOC_WATCHLIST,
                widget=SelectionWidget(format='select', label='Watchlist',
                                       label_msgid='label_watchlist',
                                       i18n_domain='plonecollectorng'),
                default='disabled',
                schemata='E-Mail'
                ),

    ))
