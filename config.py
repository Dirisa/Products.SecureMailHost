"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: config.py,v 1.19 2004/03/02 07:31:31 ajung Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneCollectorNG"
SKINS_DIR = 'skins'

GLOBALS = globals()

#
IssueWorkflowName = 'pcng_issue_workflow'
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
setDefaultRoles(EditCollectorIssue, ('Manager', 'TrackerAdmin'))
setDefaultRoles(AddCollectorIssue, ('Manager', 'TrackerAdmin'))
setDefaultRoles(AddCollectorIssueFollowup, ('Manager', 'TrackerAdmin'))
setDefaultRoles(ManageCollector, ('Manager', 'TrackerAdmin'))
setDefaultRoles(EmailSubmission, ('Manager', 'TrackerAdmin', 'Supporter'))


# Don't show the following indexes in the auto-generated searchform
SEARCHFORM_IGNOREABLE_INDEXES = ('progress_deadline', 'created', 'numberFollowups', 'getId', 'SearchableText', 'last_action')
