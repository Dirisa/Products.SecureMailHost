"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: config.py,v 1.28 2004/11/12 15:37:52 ajung Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneCollectorNG"
SKINS_DIR = 'skins'

GLOBALS = globals()

#
CollectorCatalog = 'pcng_catalog'
CollectorWorkflow = 'pcng_workflow'
CollectorTool = 'pcng_tool'
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
UNDELETEABLE_FIELDS = ('title', 'description', 'solution', 'classification', 'topic', 'importance', 'contact_email', 'contact_name')

# ATSchemaEditorNG
SCHEMA_ID = 'PloneIssueNG'
