"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Collector.py,v 1.16 2003/09/07 17:51:56 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CatalogTool import CatalogTool
from BTrees.OOBTree import OOBTree
from Products.BTreeFolder2 import CMFBTreeFolder
from Products.Archetypes.public import BaseFolder, registerType

from Transcript import Transcript, TranscriptEntry
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName
from Issue import Issue
from SchemaEditor import SchemaEditor
import collector_schema, issue_schema
import util

class Collector(BaseFolder, SchemaEditor):
    """ PloneCollectorNG """

    schema = collector_schema.schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'pcng_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'pcng_addissue',
        'name': 'Add issue',
        'action': 'add_issue',
        'permissions': (AddCollectorIssue,)
        },
        {'id': 'pcng_staff',
        'name': 'Staff',
        'action': 'pcng_staff',
        'permissions': (ManageCollector,)
        },
        {'id': 'pcng_history',
        'name': 'History',
        'action': 'pcng_history',
        'permissions': (ManageCollector,)
        },
        {'id': 'pcng_schema_editor',
        'name': 'Issue schema',
        'action': 'pcng_schema_editor',
        'permissions': (ManageCollector,)
        },
        {'id': 'pcng_notifications',
        'name': 'Notifications',
        'action': 'pcng_notifications',
        'permissions': (ManageCollector,)
        },
        {'id': 'pcng_maintainance',
        'name': 'Maintainance',
        'action': 'pcng_maintainance',
        'permissions': (ManageCollector,)
        },
        )

    __ac_roles__ = ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter')
    security = ClassSecurityInfo()

    def __init__(self, oid, **kwargs):
        BaseFolder.__init__(self, oid, **kwargs)
        self.schema_init(issue_schema.schema)
        self._num_issues = 0
        self._supporters = self._managers = self._reporters = []
        self._notification_emails = OOBTree()
        self._setup_collector_catalog()
        self.transcript = Transcript()
        self.transcript.addComment('Tracker created')

        # setup roles 
        username = util.getUserName()
        for role in ('Manager', 'TrackerAdmin', 'Owner'):
            util.add_local_role(self, username, role)

    def _setup_collector_catalog(self):
        """Create and situate properly configured collector catalog."""
        catalog = PloneCollectorNGCatalog()
        self._setObject(catalog.id, catalog)
        catalog = catalog.__of__(self)

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """

        te = TranscriptEntry()
        for name in REQUEST.form.keys():
            new = REQUEST.get(name, None)
            old = getattr(self, name, None)
            if old:
                if old != new:
                    print old,new, type(old), type(new)
                    te.addChange(name, old, new)

        self.transcript.add(te)

    ######################################################################
    # Staff handling
    ######################################################################

    security.declareProtected(ManageCollector, 'getSupporters')
    def getSupporters(self): return self._supporters

    security.declareProtected(ManageCollector, 'getManagers')
    def getManagers(self): return self._managers

    security.declareProtected(ManageCollector, 'getReporters')
    def getReporters(self): return self._reporters

    security.declareProtected(ManageCollector, 'getTrackerUsers')
    def getTrackerUsers(self):   
        """ return a list of dicts where every item of the list
            represents a user and the dict contain the necessary
            informations for the presentation.
        """

        l = []
        names = self._managers + self._supporters + self._reporters + self.acl_users.getUserNames()
        for name in util.remove_dupes(names):
            d = {}
            d['username'] = name; d['roles'] = []
            if name in self._managers: d['roles'].append('TrackerAdmin')
            if name in self._supporters: d['roles'].append('Supporter')
            if name in self._reporters: d['roles'].append('Reporter')
            l.append(d)
        return l

    security.declareProtected(ManageCollector, 'set_staff')
    def set_staff(self, reporters=[], managers=[], supporters=[], RESPONSE=None):
        """ set the staff """

        reporters.sort(); managers.sort(); supporters.sort()

        te = TranscriptEntry()
        te.addChange('managers', self._managers, managers)
        te.addChange('supporters', self._supporters, supporters)
        te.addChange('reporters', self._reporters, reporters)

        self._managers = managers
        self._reporters = reporters
        self._supporters = supporters
        self._adjust_staff_roles()

        self.transcript.add(te)

        if RESPONSE is not None: RESPONSE.redirect('pcng_view?portal_status_message=Your%20changes%20has%20been%20saved')

    def _adjust_staff_roles(self):
        """ A djust local-role assignments to track staff roster settings.
            Ie, ensure: only designated supporters and managers have 'Reviewer'
            local role, only designated managers have 'Manager' local role.
        """
        if not self._managers:
            self._managers = [getSecurityManager().getUser().getUserName()]
        util.users_for_local_role(self, self._managers, 'TrackerAdmin')
        util.users_for_local_role(self, self._supporters, 'Supporter')
        util.users_for_local_role(self, self._reporters, 'Reporter')

    def _adjust_participation_mode(self):
        """Set role privileges according to participation mode."""

        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')

        if self.participation_mode == 'authenticated':
            target_roles = target_roles + ('Authenticated', )
        elif self.participation_mode == 'anyone':
            target_roles = target_roles + ('Authenticated', 'Anonymous')

        self.manage_permission(AddCollectorIssue,
                               roles=target_roles,
                               acquire=0)

        self.manage_permission(AddCollectorIssueFollowup,
                               roles=target_roles,
                               acquire=0)

    ######################################################################
    # Notifications
    ######################################################################

    security.declareProtected(ManageCollector, 'set_notification_emails')
    def set_notification_emails(self, notifications, RESPONSE=None):
        """ set the email addresses for notifications when a workflow
            state changes.
            
            'notifications' -- record where the keys are the names of the
                        states and the values are lists of email addresses
        """

        te = TranscriptEntry()

        for state in notifications.keys():
            emails = getattr(notifications, state)
            emails = [e.strip() for e in emails if e.strip()]
            for email in emails:
                if not util.isValidEmailAddress(email):
                    raise ValueError('Invalid email address: %s' % email)

            te.addChange('notifications', self._notification_emails.get(state, []), emails)
            self._notification_emails[state] = emails

        self.transcript.add(te)
        if RESPONSE is not None: RESPONSE.redirect('pcng_view?portal_status_message=Your%20changes%20has%20been%20saved')

    security.declareProtected(ManageCollector, 'getNotificationsForState')
    def getNotificationsForState(self, state):
        """ return a of emails addresses that correspond to
            the given state.
        """
        return self._notification_emails.get(state, [])

    security.declareProtected(ManageCollector, 'issue_states')
    def issue_states(self):
        """ return a list of all related issue workflow states """

        states = getattr(self.portal_workflow, IssueWorkflowName).states._mapping.keys()
        states.sort()
        return states

    def add_issue(self, RESPONSE=None):
        """ create a new issue """
        self._num_issues += 1
        id = str(self._num_issues)
        issue = Issue(id, id, schema=self.getWholeSchema())
        issue = issue.__of__(self)
        self._setObject(id, issue)

        if RESPONSE is not None: 
            RESPONSE.redirect(self.absolute_url() + "/" + id + "/base_edit")

    ######################################################################
    # Maintainance
    ######################################################################

    def update_schema_for_issues(self, RESPONSE=None):
        """ update stored issue schema for all issues """

        schema = self.getWholeSchema()
        for issue in self.objectValues('Issue'):
            issue.updateSchema(schema)

        if RESPONSE is not None:
            RESPONSE.redirect('pcng_maintainance?portal_status_message=Issues updated')

    def reindex_issues(self, RESPONSE=None):
        """ reindex all issues """

        for issue in self.objectValues('Issue'):
            issue.reindexObject()

        if RESPONSE is not None:
            RESPONSE.redirect('pcng_maintainance?portal_status_message=Issues reindexed')

registerType(Collector)


class PloneCollectorNGCatalog(CatalogTool):
    """ catalog for collector issues """

    id = 'pcng_catalog'
    meta_type = 'PloneCollectorNG Catalog'
    portal_type = 'PloneCollectorNG Catalog'

    def enumerateIndexes(self):
        standard = CatalogTool.enumerateIndexes(self)
        custom = (('status', 'FieldIndex'),
                  ('topic', 'FieldIndex'),
                  ('subtopic', 'FieldIndex'),
                  ('classification', 'FieldIndex'),
                  ('importance', 'FieldIndex'),
                  ('security_related', 'FieldIndex'),
                  ('confidential', 'FieldIndex'),
                  ('submitter_id', 'FieldIndex'),
                  ('submitter_email', 'FieldIndex'),
                  ('version_info', 'TextIndex'),
                  ('assigned_to', 'KeywordIndex'),
                  ('deadline', 'FieldIndex'),
                  ('progress', 'FieldIndex'),
                  ('getId', 'FieldIndex'),
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        custom = ('id', 'status', 'submitter_id', 'topic', 'subtopic', 'classification',
                  'importance', 'security_related', 'confidential', 'version_info',
                  'assigned_to', 'deadline', 'progress', 'getId',
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

InitializeClass(PloneCollectorNGCatalog)
