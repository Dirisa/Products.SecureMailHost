"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: config.py,v 1.6 2003/09/20 12:42:10 ajung Exp $
"""

from Products.CMFCore.CMFCorePermissions import AddPortalContent

ADD_CONTENT_PERMISSION = AddPortalContent
PROJECTNAME = "PloneCollectorNG"
SKINS_DIR = 'skins'

GLOBALS = globals()

#
IssueWorkflowName = 'pcng_issue_workflow'

# Permissions
ManageCollector = 'Manage PloneCollectorNG'
EditCollectorIssue = 'Edit PloneCollectorNG issue'
AddCollectorIssue = 'Add PloneCollectorNG issue'
AddCollectorIssueFollowup = 'Add PloneCollectorNG issue followup'

