"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: config.py,v 1.10 2003/10/19 12:56:39 ajung Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent, setDefaultRoles

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneCollectorNG"
SKINS_DIR = 'skins'

GLOBALS = globals()

#
IssueWorkflowName = 'pcng_issue_workflow'
i18n_domain = 'plonecollectorng'

# Permissions
ManageCollector = 'Manage PloneCollectorNG'
EditCollectorIssue = 'Edit PloneCollectorNG issue'
AddCollectorIssue = 'Add PloneCollectorNG issue'
AddCollectorIssueFollowup = 'Add PloneCollectorNG issue followup'

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
