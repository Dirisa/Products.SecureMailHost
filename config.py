"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: config.py,v 1.15 2004/01/04 09:09:51 ajung Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneCollectorNG"
SKINS_DIR = 'skins'

GLOBALS = globals()

#
IssueWorkflowName = 'pcng_issue_workflow'
CollectorCatalog = 'pcng_catalog'
i18n_domain = 'plonecollectorng'

# Permissions
ManageCollector = 'PloneCollectorNG: Manage PloneCollectorNG'
EditCollectorIssue = 'PloneCollectorNG: Edit PloneCollectorNG issue'
AddCollectorIssue = 'PloneCollectorNG: Add PloneCollectorNG issue'
AddCollectorIssueFollowup = 'PloneCollectorNG: Add PloneCollectorNG issue followup'

# create new permissions and pre-assign roles 
setDefaultRoles(EditCollectorIssue, ('Manager', 'TrackerAdmin'))
setDefaultRoles(AddCollectorIssue, ('Manager', 'TrackerAdmin'))
setDefaultRoles(AddCollectorIssueFollowup, ('Manager', 'TrackerAdmin'))
setDefaultRoles(ManageCollector, ('Manager', 'TrackerAdmin'))

# Collector issue formatters for notification emails

from Products.Archetypes.public import DisplayList

VOC_ISSUE_FORMATTERS = DisplayList((
  ('format_transcript', 'Standard formatter (EN)'),
  ('format_transcript_de', 'Standard formatter (DE)'),
))


# Don't show the following indexes in the auto-generated searchform
SEARCHFORM_IGNOREABLE_INDEXES = ('progress_deadline', 'created', 'numberFollowups', 'getId', 'SearchableText')
