"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: collector_schema.py,v 1.69 2004/11/12 15:37:52 ajung Exp $
"""


from Products.Archetypes.public import DisplayList, BaseSchema, Schema
from Products.Archetypes.public import StringField, TextField, IntegerField, DateTimeField, LinesField
from Products.Archetypes.public import SelectionWidget, TextAreaWidget, IntegerWidget, MultiSelectionWidget
from Products.Archetypes.public import RichWidget, IdWidget, StringWidget, LinesWidget, InAndOutWidget

from notification_policies import VOC_NOTIFICATION_POLICIES
from workflows import VOC_WORKFLOWS
from util import readLinesFromDisk

VOC_NOTIFICATION_LANGUAGES = DisplayList((
  ('en', 'English'),
  ('cs', 'Czech'),
  ('de', 'German'),
  ('es', 'Spanish'),
  ('fi', 'Finish'),
  ('it', 'Italian'),
  ('nl', 'Dutch'),
  ('pt-br', 'Portuguese/Brazil'),
  ('ru', 'Russian'),
))

VOC_PARTICIPATION_MODE = DisplayList((
  ('staff', 'Only staff members'),
  ('authenticated', 'Any authenticated user'),                                       
  ('anyone', 'Anyone'),                                       
))

VOC_VIEW_MODE = DisplayList((
  ('restrictedstaff', 'Assigned supporters, tracker administrator and issue reporter'),
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

VOC_REFERENCES_MODE= DisplayList((
  ('disabled', 'Disabled'),
  ('enabled', 'Enabled'),
))

VOC_UPLOADS_MODE= DisplayList((
  ('disabled', 'Disabled'),
  ('enabled', 'Enabled'),
))


VOC_ISSUE_EMAIL_VERIFICATION = DisplayList((
  ('disabled', 'Disabled'),
  ('enabled', 'Enabled'),
  ('paranoid', 'Paranoid mode (reserved for later use)'),
))


VOC_WATCHLIST = DisplayList((
  ('disabled', 'Disabled'),
  ('anonymous', 'Watchlist enabled for anyone'),
  ('authenticated', 'Watchlist enabled for authenticated users'),
))

VOC_PORTLET_USAGE = DisplayList((
  ('keep', 'Keep Plone settings'),
  ('override', 'Override Plone settings'),
))

VOC_PORTLET_ACTIONS = DisplayList((
  ('left', 'Left portlet slot'),
  ('right', 'Right portlet slot'),
))

VOC_PORTLET_ISSUEDATA = DisplayList((
  ('left', 'Left portlet slot'),
  ('right', 'Right portlet slot'),
  ('inline', 'Inside issue main view'),
))

VOC_USED_PORTLETS = DisplayList((
  ('uploads', 'Uploads'),
  ('references', 'References'),
  ('search', 'Search'),
  ('searchresults', 'Search results'),
))

VOC_COLLECTOR_PORTLETS = DisplayList((
  ('Plone', 'Plone portlets'),
  ('here/pcng_portlet_macros/macros/pcng_collector_portlet', 'Collector portlet'),
))

VOC_RESULTS_REPRESENTATION = DisplayList((
  ('table', 'as table'),
  ('list', 'as flat list'),
))

VOC_NONSTAFF_TRANSCRIPT_FILTER = DisplayList((
    ('public_private', 'all transcript entries'),
    ('public_only', 'public transcript entries only') ,
))

VOC_PORTLETS = DisplayList((
  ('Plone', 'Plone portlets'),
  ('here/pcng_portlet_macros/macros/pcng_issue_portlet', 'Issue actions'),
  ('here/pcng_portlet_macros/macros/pcng_issue_uploads', 'Uploads'),
  ('here/pcng_portlet_macros/macros/pcng_issue_references', 'References'),
  ('here/pcng_portlet_macros/macros/pcng_search_portlet', 'Search'),
  ('here/pcng_portlet_macros/macros/pcng_searchresults', 'Search results'),
))


schema = BaseSchema + Schema((

    StringField('id',
                required=1,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                schemata='Main',
                widget=IdWidget(label_msgid="label_name",
                                description_msgid="help_name",
                                i18n_domain="plone"),
                ),

    StringField('title',
                required=1,
                searchable=1,
                default='',
                accessor='Title',
                schemata='Main',
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
                schemata='Main',
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

    IntegerField('deadline_tickets',
                default=14,
                widget=StringWidget(label='Automatic deadline in days for new issues',
                                    label_msgid='label_deadline_tickets',
                                    i18n_domain='plonecollectorng'),
                schemata='Main',
                ),
    StringField('collector_workflow',
                vocabulary=VOC_WORKFLOWS,
                default='pcng_issue_workflow (PloneCollectorNG default workflow)',
                widget=SelectionWidget(format='select', 
                                       label='Workflow (change the workflow *only* for empty collectors)',
                                       label_msgid='label_workflow',
                                       i18n_domain='plonecollectorng'),
                schemata='Main'
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
                                    label='Issue submissions through email',
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
                schemata='Main'
                ),

    StringField('references_mode',
                vocabulary=VOC_REFERENCES_MODE,
                widget=SelectionWidget(format='select', 
                                       label='References between issues',
                                       label_msgid='label_references',
                                       i18n_domain='plonecollectorng'),
                default='disabled',
                schemata='Main'
                ),

    StringField('uploads_mode',
                vocabulary=VOC_UPLOADS_MODE,
                widget=SelectionWidget(format='select', 
                                       label='File/Image uploads',
                                       label_msgid='label_file_image_uploads',
                                       i18n_domain='plonecollectorng'),
                default='enabled',
                schemata='Main'
                ),

    StringField('portlet_issuedata',
                vocabulary=VOC_PORTLET_ISSUEDATA,
                widget=SelectionWidget(format='select', 
                                       label='Portlet issue data',
                                       label_msgid='label_portlet_issuedata',
                                       i18n_domain='plonecollectorng'),
                default='inline',
                schemata='Look and Feel'
                ),

    LinesField('collector_portlets_left',
                vocabulary=VOC_COLLECTOR_PORTLETS,
                widget=InAndOutWidget(size=5,
                                      label='Collector portlets left side',
                                      label_msgid='label_collector_portlets_left',
                                      i18n_domain='plonecollectorng'),
                default=['Plone', 'here/pcng_portlet_macros/macros/pcng_collector_portlet'],
                schemata='Look and Feel'
                ),

    LinesField('collector_portlets_right',
                vocabulary=VOC_COLLECTOR_PORTLETS,
                widget=InAndOutWidget(size=5,
                                      label='Collector portlets right side',
                                      label_msgid='label_collector_portlets right',
                                      i18n_domain='plonecollectorng'),
                default=['Plone', 'here/pcng_portlet_macros/macros/pcng_collector_portlet'],
                schemata='Look and Feel'
                ),

    LinesField('portlets_left',
                vocabulary=VOC_PORTLETS,
                widget=InAndOutWidget(size=5,
                                      label='Issue portlets left side',
                                      label_msgid='label_portlet_issues_left',
                                      i18n_domain='plonecollectorng'),
                default=['Plone', 'here/pcng_portlet_macros/macros/pcng_issue_portlet'],
                schemata='Look and Feel'
                ),

    LinesField('portlets_right',
                vocabulary=VOC_PORTLETS,
                widget=InAndOutWidget(size=5,
                                      label='Issue portlets right side',
                                      label_msgid='label_portlet_issues_right',
                                      i18n_domain='plonecollectorng'),
                default=['Plone'],
                schemata='Look and Feel'
                ),

    StringField('results_representation',
                vocabulary=VOC_RESULTS_REPRESENTATION,
                widget=SelectionWidget(size=1,
                                      format='select',
                                      label='Representation of search results',
                                      label_msgid='label_results_representation',
                                      i18n_domain='plonecollectorng'),
                default='list',
                schemata='Look and Feel'
                ),

    StringField('participation_mode',
                vocabulary=VOC_PARTICIPATION_MODE,
                widget=SelectionWidget(format='select', 
                                       label='Participation mode (who can file issues)',
                                       label_msgid='label_participation_mode',
                                       i18n_domain='plonecollectorng'),
                default='staff',
                schemata='Permissions',
                ),

    StringField('view_mode',
                vocabulary=VOC_VIEW_MODE,
                widget=SelectionWidget(format='select', 
                                       label='View mode (who can view issues)',
                                       label_msgid='label_view_mode',
                                       i18n_domain='plone#collectorng'),
                default='staff',
                schemata='Permissions',
                ),
    
    StringField('nonstaff_transcript_filter',
                vocabulary=VOC_NONSTAFF_TRANSCRIPT_FILTER,
                widget=SelectionWidget(format='select', 
                                       label='Transcript entries visible to non-staff members',
                                       label_msgid='label_view_mode',
                                       i18n_domain='plonecollectorng'),
                default='public_only',
                schemata='Permissions',
                ),

    IntegerField('upload_limit',
                widget=StringWidget(label='Maximum size for uploaded files in bytes',
                                     label_msgid='label_maximum_size_for_uploads',
                                     i18n_domain='plonecollectorng'),
                default=200000,
                schemata='Permissions',
                ),


    LinesField('phrases',
                widget=LinesWidget(rows=15,
                                   label='Followup phrases',
                                   label_msgid='label_followup_phrases',
                                   i18n_domain='plonecollectorng'),
                default=readLinesFromDisk('phrases.txt'),
                schemata='Phrases'
                ),
    ))
