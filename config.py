"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: config.py,v 1.25 2004/09/27 15:40:35 ajung Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneCollectorNG"
SKINS_DIR = 'skins'

GLOBALS = globals()

#
CollectorCatalog = 'pcng_catalog'
CollectorWorkflow = 'pcng_workflow'
i18n_domain = 'plonecollectorng'

# Permissions
ManageCollector = 'PloneCollectorNG: Manage PloneCollectorNG'
EditCollectorIssue = 'PloneCollectorNG: Edit PloneCollectorNG issue'
AddCollectorIssue = 'PloneCollectorNG: Add PloneCollectorNG issue'
AddCollectorIssueFollowup = 'PloneCollectorNG: Add PloneCollectorNG issue followup'
EmailSubmission = 'PloneCollectorNG: Submit issue through email'

# create new permissions and pre-assign roles 
setDefaultRoles(EditCollectorIssue, ('Manager', 'TrackerAdmin', 'Supporter'))
setDefaultRoles(AddCollectorIssue, ('Manager', 'TrackerAdmin'))
setDefaultRoles(AddCollectorIssueFollowup, ('Manager', 'TrackerAdmin'))
setDefaultRoles(ManageCollector, ('Manager', 'TrackerAdmin'))
setDefaultRoles(EmailSubmission, ('Manager', 'EmailSubmitter'))

# Don't show the following indexes in the auto-generated searchform
SEARCHFORM_IGNOREABLE_INDEXES = ('progress_deadline', 'created', 'numberFollowups', 'getId', 'SearchableText', 'last_action')

# These fields can not be deleted through the SchemaEditor
UNDELETEABLE_FIELDS = ('title', 'description', 'classification', 'topic', 'importance', 'contact_email', 'contact_name')

# ATSchemaEditorNG
SCHEMA_ID = 'PloneIssueNG'
