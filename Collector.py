"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Collector.py,v 1.46 2003/10/19 12:55:45 ajung Exp $
"""

from Globals import InitializeClass
from AccessControl import  ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CatalogTool import CatalogTool
from BTrees.OOBTree import OOBTree
from Products.BTreeFolder2 import CMFBTreeFolder
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import OrderedDict
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import setDefaultRoles, ModifyPortalContent

from Transcript import Transcript
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup, EditCollectorIssue
from config import IssueWorkflowName
from Issue import PloneIssueNG
from SchemaEditor import SchemaEditor
from OrderedSchema import OrderedBaseFolder, OrderedSchema
from Translateable import Translateable
import collector_schema 
import issue_schema
import util

class PloneCollectorNG(OrderedBaseFolder, SchemaEditor, Translateable):
    """ PloneCollectorNG """

    schema = collector_schema.schema

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'pcng_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'edit',
        'name': 'Edit',
        'action': 'portal_form/pcng_base_edit',
        'permissions': (ManageCollector,)
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
        {'id': 'pcng_member_preferences',
        'name': 'Member preferences',
        'action': 'pcng_member_preferences',
        'permissions': (CMFCorePermissions.SetOwnProperties,)
        },
        )

    __ac_roles__ = ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter')
    security = ClassSecurityInfo()

    def __init__(self, oid, **kwargs):
        OrderedBaseFolder.__init__(self, oid, **kwargs)
        self.initializeArchetype()
        self.schema_init(issue_schema.schema)
        self._num_issues = 0
        self._supporters = self._managers = self._reporters = []
        self._notification_emails = OOBTree()
        self._setup_collector_catalog()

        # setup roles 
        username = util.getUserName()
        for role in ('Manager', 'TrackerAdmin', 'Owner'):
            util.addLocalRole(self, username, role)

    def manage_afterAdd(self, item, container):
        """ post creation actions """
        self._transcript = Transcript()
        self._transcript.addComment('Tracker created')

        # Archestypes uses hardcoded factory-settings for 'immediate_view'
        # that don't not meet our requirements to jump into the 'view' 
        # from the navigation tree instead into 'edit'. So we tweak
        # 'immediate_view' a bit.
        typestool = getToolByName(self, 'portal_types', None)
        ti = typestool.getTypeInfo('PloneIssueNG')
        ti.immediate_view = 'pcng_issue_view'
        ti = typestool.getTypeInfo('PloneCollectorNG')
        ti.immediate_view = 'pcng_view'
        
    def _setup_collector_catalog(self):
        """Create and situate properly configured collector catalog."""
        catalog = PloneCollectorNGCatalog()
        self._setObject(catalog.getId(), catalog)
        catalog = catalog.__of__(self)

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """

        for name in REQUEST.form.keys():
            new = REQUEST.get(name, None)
            old = getattr(self, name, None)
            if old:
                if str(old) != str(new): # Archetypes does not use Zope converters
                    self._transcript.addChange(name, old, new)

    ######################################################################
    # Transcript
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'getTranscript')
    def getTranscript(self):
        """ return the Transcript instance """
        return self._transcript

    ######################################################################
    # Staff handling
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'getSupporters')
    def getSupporters(self): return self._supporters

    security.declareProtected(CMFCorePermissions.View, 'getManagers')
    def getManagers(self): return self._managers

    security.declareProtected(CMFCorePermissions.View, 'getReporters')
    def getReporters(self): return self._reporters

    security.declareProtected(CMFCorePermissions.View, 'getTrackerUsers')
    def getTrackerUsers(self, staff_only=0):   
        """ return a list of dicts where every item of the list
            represents a user and the dict contain the necessary
            informations for the presentation.
        """

        l = []
        membership_tool = getToolByName(self, 'portal_membership', None)
        names = self._managers + self._supporters + self._reporters
        if not staff_only:
            folder = self
            running = 1
            while running:     # search for acl_users folders
                if hasattr(folder, 'acl_users'):
                    usernames = folder.acl_users.getUserNames()
                    for name in usernames:
                        if not name in names:
                            names.append(name)

                if len(folder.getPhysicalPath()) == 1:
                    running = 0
                folder = folder.aq_parent

        for name in util.remove_dupes(names):
            member = membership_tool.getMemberById(name)
            d = { 'username':name, 'roles':[], 'fullname':'', 'email':''}

            if member:
                d['fullname'] = member.getProperty('fullname')
                d['email'] = member.getProperty('email')
            
            if name in self._managers: d['roles'].append('TrackerAdmin')
            if name in self._supporters: d['roles'].append('Supporter')
            if name in self._reporters: d['roles'].append('Reporter')
            l.append(d)

        return l

    security.declareProtected(ManageCollector, 'set_staff')
    def set_staff(self, reporters=[], managers=[], supporters=[], RESPONSE=None):
        """ set the staff """

        reporters.sort(); managers.sort(); supporters.sort()

        self._transcript.addIncrementalChange('managers', self._managers, managers)
        self._transcript.addIncrementalChange('supporters', self._supporters, supporters)
        self._transcript.addIncrementalChange('reporters', self._reporters, reporters)

        self._managers = managers
        self._reporters = reporters
        self._supporters = supporters
        self._adjust_staff_roles()

        util.redirect(RESPONSE, 'pcng_view', 'Your changes has been saved')

    def _adjust_staff_roles(self):
        """ Adjust local-role assignments to track staff roster settings.
            Ie, ensure: only designated supporters and managers have 'Reviewer'
            local role, only designated managers have 'Manager' local role.
        """
        if not self._managers:
            self._managers = [util.getUserName()]
        util.adjustLocalRoles(self, self._managers, 'TrackerAdmin')
        util.adjustLocalRoles(self, self._supporters, 'Supporter')
        util.adjustLocalRoles(self, self._reporters, 'Reporter')

    def _adjust_participation_mode(self):
        """Set role privileges according to participation mode."""

        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')

        if self.participation_mode == 'authenticated':
            target_roles += ('Authenticated', )
        elif self.participation_mode == 'anyone':
            target_roles += ('Authenticated', 'Anonymous')

        for p in (AddCollectorIssue, AddCollectorIssueFollowup, ModifyPortalContent):
            self.manage_permission(p, roles=target_roles, acquire=0)


    def _adjust_view_mode(self):
        """Set role privileges according to view mode."""

        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')

        if self.view_mode == 'authenticated':
            target_roles += ('Authenticated', )
        elif self.view_mode == 'anyone':
            target_roles += ('Authenticated', 'Anonymous')

        self.manage_permission(CMFCorePermissions.View, roles=target_roles, acquire=0)

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

        for state in notifications.keys():
            emails = getattr(notifications, state)
            emails = [e.strip() for e in emails if e.strip()]
            for email in emails:
                if not util.isValidEmailAddress(email):
                    raise ValueError('Invalid email address: %s' % email)

            self._transcript.addChange('notifications', self._notification_emails.get(state, []), emails)
            self._notification_emails[state] = emails

        util.redirect(RESPONSE, 'pcng_view', 'Your changes has been saved')

    security.declareProtected(ManageCollector, 'getNotificationsForState')
    def getNotificationsForState(self, state):
        """ return a of emails addresses that correspond to the given state.  """
        return self._notification_emails.get(state, [])

    security.declareProtected(CMFCorePermissions.View, 'issue_states')
    def issue_states(self):
        """ return a list of all related issue workflow states """
        wftool = getToolByName(self, 'portal_workflow')
        states = wftool[IssueWorkflowName].states._mapping.keys()
        states.sort()
        return states

    def add_issue(self, RESPONSE=None):
        """ create a new issue """
        self._num_issues += 1
        id = str(self._num_issues)
        issue = PloneIssueNG(id, '', self.schema_getWholeSchema())
        issue = issue.__of__(self)
        self._setObject(id, issue)

        util.redirect(RESPONSE, self.absolute_url() + "/" + id + "/pcng_base_edit", 
                      portal_status_message='New issue created',
                      fieldset='issuedata')

    ######################################################################
    # Maintainance
    ######################################################################

    def reindexObject(self, idxs=None):
        """ hook for reindexing the object """
        OrderedBaseFolder.reindexObject(self)
        self._adjust_view_mode()           # can we hook this somewhere else?
        self._adjust_participation_mode()

    security.declareProtected(CMFCorePermissions.View, 'getNumberIssues')
    def getNumberIssues(self):
        """ return the number of issues """
        return len(self.objectIds('PloneIssueNG'))
    __len__ = getNumberIssues

    security.declareProtected(ManageCollector, 'update_schema_for_issues')
    def update_schema_for_issues(self, REQUEST=None, RESPONSE=None):
        """ update stored issue schema for all issues """

        schema = self.schema_getWholeSchema()
        for issue in self.objectValues('PloneIssueNG'):
            if hasattr(issue, '_v_schema'):
                issue._v_schema = None

        util.redirect(RESPONSE, REQUEST['HTTP_REFERER'], 'Issues updated')

    security.declareProtected(ManageCollector, 'reindex_issues')
    def reindex_issues(self, RESPONSE=None):
        """ reindex all issues """
        for issue in self.objectValues('PloneIssueNG'):
            issue.reindexObject()
        util.redirect(RESPONSE, 'pcng_maintainance', 'Issues reindexed')

    ######################################################################
    # Some Archetypes madness
    ######################################################################

    def Schemata(self):
        """ we need to override Schemata() to provide support
            for ordered fields.
        """

        schemata = OrderedDict()
        for f in self.schema.fields():
            sub = schemata.get(f.schemata, OrderedSchema(name=f.schemata))
            sub.addField(f)
            schemata[f.schemata] = sub
        return schemata

    def test(self):
        """ some test """
        return self.translate('label_description', 'this is a test')

registerType(PloneCollectorNG)


class PloneCollectorNGCatalog(CatalogTool):
    """ catalog for collector issues """

    id = 'pcng_catalog'
    meta_type = 'PloneCollectorNG Catalog'
    portal_type = 'PloneCollectorNG Catalog'

    def enumerateIndexes(self):
        standard = CatalogTool.enumerateIndexes(self)
        custom = (('status', 'FieldIndex'),
                  ('importance', 'FieldIndex'),
                  ('classification', 'FieldIndex'),
                  ('topic', 'FieldIndex'),
                  ('assigned_to', 'KeywordIndex'),
                  ('progress_deadline', 'FieldIndex'),
                  ('getId', 'FieldIndex'),
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""
        standard = CatalogTool.enumerateColumns(self)
        custom = ('id', 'status', 'topic', 'classification',
                  'importance', 'assigned_to', 'progress_deadline', 'getId',
                  )
        custom = tuple([col for col in custom if col not in standard])
        return standard + custom


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('syndication','references','metadata'):
            a['visible'] = 0
    return fti

InitializeClass(PloneCollectorNGCatalog)
