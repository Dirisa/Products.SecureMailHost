"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Collector.py,v 1.218 2004/10/08 16:11:59 ajung Exp $
"""

import base64, time, random, md5, os, urllib

from DateTime import DateTime
from BTrees.OOBTree import OOBTree
from ZODB.POSException import ConflictError
from AccessControl import  ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Products.Archetypes.public import registerType
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import *
from Products.PythonScripts.PythonScript import PythonScript

from Products.ATSchemaEditorNG.SchemaEditor import SchemaEditor
from config import CollectorCatalog, SEARCHFORM_IGNOREABLE_INDEXES, CollectorWorkflow
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup, EditCollectorIssue, EmailSubmission
from config import UNDELETEABLE_FIELDS, SCHEMA_ID
from Products.PloneCollectorNG.WorkflowTool import WorkflowTool
from Products.Archetypes.BaseBTreeFolder import BaseBTreeFolder
from Transcript2 import Transcript2, CommentEvent, ChangeEvent, IncrementalChangeEvent
import notifications, collector_schema, issue_schema, util
from Issue import PloneIssueNG
from Translateable import Translateable
from Catalog import PloneCollectorNGCatalog
from workflows import VOC_WORKFLOWS


class PloneCollectorNG(BaseBTreeFolder, SchemaEditor, Translateable):
    """ PloneCollectorNG """

    schema = collector_schema.schema
    archetype_name = 'PCNG Tracker'
    default_view = 'pcng_view'
    immediate_view = 'pcng_view'

    actions = ({
        'id': 'pcng_browse',
        'name': 'Browse issues',
        'action': 'pcng_view',
        'permissions': (View,),
        'category' : 'object_pcng_collector',
        },
        {'id': 'pcng_search_form',
        'name': 'New search',
        'action': 'pcng_search_form',
        'permissions': (View,),
        'category' : 'object_pcng_collector',
        },
        {'id': 'pcng_configuration',
        'name': 'Configuration',
        'action': 'pcng_configuration',
        'permissions': (ManageCollector,),
        'category' : 'object_pcng_collector',
        },
        {'id': 'pcng_addissue',
        'name': 'Add issue',
        'action': 'redirect_create_object',
        'permissions': (AddCollectorIssue,),
        'category' : 'object_pcng_collector',
        },
        {'id': 'pcng_history',
        'name': 'History',
        'action': 'pcng_history',
        'permissions': (ManageCollector,),
        'category' : 'object_pcng_collector',
        },
        {'id': 'pcng_reports',
        'name': 'Reports',
        'action': 'pcng_reports',
        'permissions': (ManageCollector,),
        'category' : 'object_pcng_collector',
        },
        {'id': 'collector_debug',
        'name': 'Debug',
        'action': 'pcng_debug',
        'permissions': (ManageCollector,)
        },
        )

    __ac_roles__ = ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter')
    security = ClassSecurityInfo()

    def manage_afterAdd(self, item, container):
        """ post creation (or post renaming) actions """
        BaseBTreeFolder.manage_afterAdd(self, item, container)

        # ATSchemaEditorNG
        self.atse_init()
        self.atse_registerSchema(SCHEMA_ID,
                                 issue_schema.schema,
                                 filtered_schemas=('default', 'metadata'),
                                 undeleteable_fields = UNDELETEABLE_FIELDS,
                                 domain='plonecollectorng')   
        self._num_issues = 0
        self._supporters = self._managers = self._reporters = []
        self._notification_emails = OOBTree()

        # setup local roles for creator
        username = util.getUserName()
        for role in ('Manager', 'TrackerAdmin', 'Owner'):
            util.addLocalRole(self, username, role)

        if getattr(self, '_already_created', 0) == 0:
            # Upon creation we need to add the transcript
            self._transcript2 = Transcript2().__of__(self)
            self._transcript2.add(CommentEvent(u'Tracker created', state='system'))
            self._already_created = 1
        else:
            # manager_afterAdd() is also called when the collector is
            # renamed. So we reindex the issues automatically
            self.reindex_issues()

        self.setup_tools()

        # high-security token for email notifications
        self.createToken()

    def manage_beforeDelete(self, item, container):
        """ Hook for pre-deletion actions """
        self.unindexObject()

    security.declareProtected(ManageCollector, 'setup_tools')
    def setup_tools(self, RESPONSE=None):
        """ setup up required tools """

        self._setup_catalog()
        self._setup_workflow()
        self.getTranscript().add(CommentEvent(u'Tool setup', state='system'))

        if RESPONSE:
            util.redirect(RESPONSE, 'pcng_maintenance',
                          self.Translate('tools_recreated', 'Tools recreated'))

    def _setup_catalog(self):
        """ setup catalog tool """

        try: self.manage_delObjects(CollectorCatalog)
        except ConflictError: raise
        except: pass

        catalog = PloneCollectorNGCatalog()
        self._setObject(catalog.getId(), catalog)
        catalog = catalog.__of__(self)

    def _setup_workflow(self):
        """ setup workflow tool """

        try: self.manage_delObjects(CollectorWorkflow)
        except ConflictError: raise
        except: pass

        wf = WorkflowTool()
        self._setObject(CollectorWorkflow, wf)
        wf = wf.__of__(self)

        wf_tool = getToolByName(self, CollectorWorkflow)
        # Get the workflow ID from the instance
        wf_id = self.getField('collector_workflow').get(self)
        wf_type = VOC_WORKFLOWS.getValue(wf_id)
        wf_tool.manage_addWorkflow(id=wf_id, workflow_type=wf_id)

        # Assign PythonScript for workflows
        for id in ('addAssignees', 'send_notifications'):
            script = PythonScript(id)
            script.write(open(os.path.join(os.path.dirname(__file__), 'workflows', 'scripts', id +'.py')).read())
            try:
                self.manage_delObjects(id)
            except: pass
            wf_tool[wf_id].scripts._setObject(id, script)
            getattr(wf_tool[wf_id].scripts, id)._proxy_roles = ('Manager', )

        wf_tool.setChainForPortalTypes(('PloneIssueNG',), wf_id)

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """

        # check for changes in workflow
        if REQUEST.has_key('collector_workflow'):
            new_wf = REQUEST['collector_workflow']
            if new_wf != self.getCollector_workflow() and len(self) > 0:
                raise RuntimeError(self.Translate('unable_changing_workflows', 
                                                  'Unable to change the workflow for non-empty collectors'))

        field_names = [ f.getName() for f in self.Schema().fields()]
        for name in REQUEST.form.keys():
            if not name in field_names: continue
            new = REQUEST.get(name, None)
            old = self.getField(name).get(self)
            if old:
                if str(old) != str(new): # Archetypes does not use Zope converters
                    self.getTranscript().add(ChangeEvent(name, old, new))


    ######################################################################
    # Transcript
    ######################################################################

    security.declareProtected(View, 'getTranscript')
    def getTranscript(self):
        """ return the Transcript instance """
        return self._transcript2

    ######################################################################
    # Staff handling
    ######################################################################

    security.declareProtected(View, 'getSupporters')
    def getSupporters(self): return self._supporters

    security.declareProtected(View, 'getManagers')
    def getManagers(self): return self._managers

    security.declareProtected(View, 'getReporters')
    def getReporters(self): return self._reporters

    security.declareProtected(View, 'getTrackerUsers')
    def getTrackerUsers(self, staff_only=0, unassigned_only=0, with_groups=0):
        """ return a list of dicts where every item of the list
            represents a user and the dict contain the necessary
            informations for the presentation.
        """

        membership_tool = getToolByName(self, 'portal_membership', None)

        staff = self._managers + self._supporters + self._reporters

        all_names = []
        folder = self
        running = 1
        while running:     # search for acl_users folders
            if hasattr(folder, 'acl_users'):
                usernames = folder.acl_users.getUserNames()
                for name in usernames:
                    if not name in all_names:
                        all_names.append(name)

            if len(folder.getPhysicalPath()) == 1:
                running = 0
            folder = folder.aq_parent

        # Filter out non-existing users
        staff = [s for s in staff if s in all_names]

        if staff_only:
            names = staff
        else:
            names = all_names + staff

        l = []
        groups = self.pcng_get_groups()  # get group IDs from GRUF
        for name in util.remove_dupes(names):
            if name.replace('group_', '') in groups and not with_groups: continue  # no group names !!!
            member = membership_tool.getMemberById(name)
            d = { 'username':name, 'role':'', 'fullname':'', 'email':''}

            if member:
                d['fullname'] = member.getProperty('fullname')
                d['email'] = member.getProperty('email')

            if name in self._reporters: d['role'] = 'Reporter'
            if name in self._supporters: d['role'] = 'Supporter'
            if name in self._managers: d['role'] = 'TrackerAdmin'
            l.append(d)

        l.sort(lambda a,b: cmp(a['username'].lower(), b['username'].lower()))

        if staff_only:
            return [item for item in l if item['username'] in staff]
        elif unassigned_only:
            return [item for item in l if item['username'] not in staff]
        else:
            return l

    security.declareProtected(ManageCollector, 'set_staff')
    def set_staff(self, reporters=[], managers=[], supporters=[], RESPONSE=None):
        """ set the staff """

        reporters.sort(); managers.sort(); supporters.sort()

        self.getTranscript().add(IncrementalChangeEvent('managers', self._managers, managers))
        self.getTranscript().add(IncrementalChangeEvent('supporters', self._supporters, supporters))
        self.getTranscript().add(IncrementalChangeEvent('reporters', self._reporters, reporters))

        self._managers = managers
        self._reporters = reporters
        self._supporters = supporters
        self._adjust_staff_roles()
        self._adjust_participation_mode()

        util.redirect(RESPONSE, 'pcng_staff',
                      self.Translate('changes_saved', 'Your changes have been saved'))

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

        if self.participation_mode == 'authenticated':
            add_roles = ('Authenticated', )
        elif self.participation_mode == 'anyone':
            add_roles = ('Authenticated', 'Anonymous')
        else:
            add_roles = ()

        # AddCollectorIssue
        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Owner')
        self.manage_permission(AddCollectorIssue, roles=target_roles+add_roles, acquire=0)
        self.manage_permission(AddPortalContent, roles=target_roles+add_roles, acquire=0)

        # AddCollectorIssueFollowup
        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Owner')
        self.manage_permission(AddCollectorIssueFollowup, roles=target_roles+add_roles, acquire=0)

        # ModifyPortalContent
        target_roles = ('Supporter','TrackerAdmin', 'Manager', 'Owner')
        self.manage_permission(ModifyPortalContent, roles=target_roles+add_roles, acquire=0)
        self.manage_permission(EditCollectorIssue, roles=target_roles, acquire=0)

    def _adjust_view_mode(self):
        """Set role privileges according to view mode."""

        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')

        view_mode = self.getView_mode()
        if view_mode == 'authenticated':
            target_roles += ('Authenticated', )
        elif view_mode == 'anyone':
            target_roles += ('Authenticated', 'Anonymous')

        self.manage_permission(View, roles=target_roles, acquire=0)

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
                    raise ValueError(self.Translate('invalid_email_address',
                                                    'Invalid email address: $email', email=email))

            self.getTranscript().add(ChangeEvent('notifications', self._notification_emails.get(state, []), emails))
            self._notification_emails[state] = emails

        util.redirect(RESPONSE, 'pcng_view',
                      self.Translate('changes_saved', 'Your changes have been saved'))

    security.declareProtected(ManageCollector, 'getNotificationsForState')
    def getNotificationsForState(self, state):
        """ return a of emails addresses that correspond to the given state.  """
        return self._notification_emails.get(state, [])

    security.declareProtected(View, 'issue_states')
    def issue_states(self):
        """ return a list of all related issue workflow states """
        wftool = getToolByName(self, CollectorWorkflow)
        states = wftool[self.collector_workflow].states._mapping.keys()
        states.sort()
        return states

    security.declareProtected(AddCollectorIssue, 'new_issue_number')
    def new_issue_number(self):
        """ return a new issue number"""
        self._num_issues += 1
        return str(self._num_issues)

    security.declareProtected(View, 'get_current_issue_number')
    def get_current_issue_number(self):
        """ return a new issue number"""
        return self._num_issues

    security.declareProtected(ManageCollector, 'set_current_issue_number')
    def set_current_issue_number(self, num):
        """ set the issue number """
        self._num_issues = int(num)

    security.declareProtected(AddCollectorIssue, 'redirect_create_object')
    def redirect_create_object(self, RESPONSE=None):
        """ Create a new issue as temporary object inside a temporary folder to
            avoid unfilled issues. We do no longer support portal_factory because
            it raises more problems than it solves.
        """

        from Products.TemporaryFolder.TemporaryFolder import constructTemporaryFolder
        if not hasattr(self, 'temp'):
            constructTemporaryFolder(self, 'temp')
        temp = getattr(self, 'temp')
        id = '%s_%f' % (self.Translate('new_issue', 'NewIssue'), time.time() * random.random())
        issue = PloneIssueNG(id)
        temp._setObject(id, issue)
        issue = issue.__of__(temp)
        # remove pending issues
        pending = [issue.getId() for issue in temp.objectValues('PloneIssueNG') if DateTime() - issue.bobobase_modification_time() > 2*3600]
        temp.manage_delObjects(pending)
        # if more than 50 issues in memory, remove the first 25
        if len(temp.objectIds()) > 50:
            pending = temp.objectValues('PloneIssueNG')
            pending.sort(lambda x,y: cmp(x.bobobase_modification_time(), y.bobobase_modification_time()))
            temp.manage_delObjects([o.getId() for o in pending[:25]])
        RESPONSE.redirect(issue.absolute_url() + '/pcng_base_edit')

    createObject = redirect_create_object

    def move_temporary_issue(self, issue, new_id):
        """ Move a temporay issue from the temp folder """
        tempfolder = issue.aq_parent
        self.manage_pasteObjects(tempfolder.manage_copyObjects([issue.getId()]))
        self.manage_renameObjects([issue.getId()], [new_id])
        tempfolder.manage_delObjects([issue.getId()])
        issue = getattr(self, new_id)
        issue = issue.__of__(self)
        issue.reindexObject()
        return issue

    security.declareProtected(AddCollectorIssue, 'add_issue')
    def add_issue(self, RESPONSE=None):
        """ create a new issue """
        id = self.new_issue_number()
        self.invokeFactory('PloneIssueNG', id)
        issue = self._getOb(id)
        util.redirect(RESPONSE, self.absolute_url() + "/" + id + "/pcng_base_edit",
                      portal_status_message=self.Translate('new_issue_created', 'New issue created'),
                      fieldset='issuedata')
        if RESPONSE is None:
            return id

    def view(self, REQUEST=None, RESPONSE=None):
        """ override 'view' """

        if REQUEST and REQUEST.get('fieldset', None):
            fieldset = REQUEST.get('fieldset', None)
            util.redirect(REQUEST.RESPONSE, 'pcng_base_edit',
                          portal_status_message=REQUEST.get('portal_status_message', ''),
                          fieldset=fieldset)
        else:
            return self.pcng_view(REQUEST=REQUEST, RESPONSE=RESPONSE)

    base_view = view

    ######################################################################
    # Searchform editor
    ######################################################################

    security.declareProtected(View, 'getIndexes')
    def getIndexes(self):
        """ return a sequence of tuples (indexId, indexType)"""

        return [ (id, idx.meta_type)
                 for id, idx in getToolByName(self, CollectorCatalog)._catalog.indexes.items()
                 if not id in SEARCHFORM_IGNOREABLE_INDEXES ]

    ######################################################################
    # Topic-user mapping
    ######################################################################

    security.declareProtected(ManageCollector, 'set_topic_users')
    def set_topic_users(self, topic, users):
        """Set the topics-user mapping for 'topic' where 'users' is a list
           of user IDs.
        """

        if not hasattr(self, '_topic_user'):
            self._topic_user = OOBTree()
        self._topic_user[topic] = users

    security.declareProtected(View, 'get_topics_user')
    def get_topics_user(self):
        """Return the topic-user mapping """
        if not hasattr(self, '_topic_user'):
            self._topic_user = OOBTree()

        d = {}
        for k,v in self._topic_user.items():
            d[k] = v
        return d

    ######################################################################
    # GroupUserFolder
    ######################################################################

    security.declareProtected(View, 'get_gruf_groups')
    def get_gruf_groups(self):
        """ return list of GRUF group IDs """

        GT = getToolByName(self, 'portal_groups', None)
        if GT is None: return ()
        return GT.listGroupIds()

    ######################################################################
    # Maintainance
    ######################################################################

    def reindexObject(self, idxs=None):
        """ hook for reindexing the object """
        BaseBTreeFolder.reindexObject(self)
        self._adjust_view_mode()           # can we hook this somewhere else?
        self._adjust_participation_mode()

    security.declareProtected(ManageCollector, 'reindex_issues')
    def reindex_issues(self, RESPONSE=None):
        """ reindex all issues """

        for issue in self.objectValues('PloneIssueNG'): issue.reindexObject()
        self.getTranscript().add(CommentEvent(u'Issues reindexed', state='system'))
        util.redirect(RESPONSE, 'pcng_maintenance', 
                      self.Translate('issues_reindexed', 'Issues reindexed'))

    security.declareProtected(View, 'getNumberIssues')
    def getNumberIssues(self):
        """ return the number of issues """
        return len(self.objectIds(('PloneIssueNG',)))
    __len__ = getNumberIssues

    def __nonzero__(self): return 1

    security.declareProtected(ManageCollector, 'resetNumberIssues')
    def resetNumberIssues(self, RESPONSE=None):
        """ reset number of issues """
        self._num_issues = 0
        self.getTranscript().add(CommentEvent(u'Number of issues reset to 0', state='system'))
        util.redirect(RESPONSE, 'pcng_maintenance', 
                      self.Translate('number_issues_reseted', 'Issue number reseted to 0'))

    security.declareProtected(ManageCollector, 'update_all_schemas')
    def update_all_schemas(self, return_to=None, REQUEST=None, RESPONSE=None):
        """ update stored issue schema for all issues """

        for issue in self.objectValues(('PloneIssueNG',)):
            if hasattr(issue, '_v_schema'):
                issue._v_schema = None

        self.getTranscript().add(CommentEvent(u'Issue schemas reseted', state='system'))
        if return_to:
            util.redirect(RESPONSE, return_to,
                          self.Translate('issues_updated', 'Issues updated'))
        else:
            util.redirect(RESPONSE, 'pcng_schema_editor',
                          self.Translate('issues_updated', 'Issues updated'))

    security.declareProtected(ManageCollector, 'update_collector_schema')
    def update_collector_schema(self, RESPONSE=None):
        """ check the attributes of the collector instance against the
            current schema and update attributes accordingly.
        """

        for field in self.Schema().fields():

            try:
                value = field.get(self)
            except ConflictError:
                pass
            except:
                field.set(self, field.default)

        self.getTranscript().add(CommentEvent(u'Collector schema updated', state='system'))
        util.redirect(RESPONSE, 'pcng_maintenance',
                          self.Translate('collector_schema_updated', 'Collector schema updated'))

    security.declareProtected(ManageCollector, 'register_issue_uids')
    def register_issue_uids(self, RESPONSE=None):
        """ Issues imported through a .zexp file don't have UIDs anymore.
            They must be re-registered with the reference_catalog of AT.
        """

        from Products.Archetypes.config import REFERENCE_CATALOG
        RC = getToolByName(self, REFERENCE_CATALOG)

        for issue in self.objectValues('PloneIssueNG'):
            if issue.UID() is None:
                RC.registerObject(issue)
      
        self.getTranscript().add(CommentEvent(u'Issue UIDs reregistered', state='system'))
        util.redirect(RESPONSE, 'pcng_maintenance',
                      self.Translate('uids_recreated', 'UIDs recreated'))

    security.declareProtected(View, 'asPDF')
    def asPDF(self, ids, RESPONSE):
        """ Produce a PDF for all issues in 'ids'"""
        import pdfwriter

        pdf = pdfwriter.pdfwriter(self, ids)
        RESPONSE.setHeader('content-type', 'application/pdf')
        RESPONSE.setHeader('content-length', str(len(pdf)))
        RESPONSE.setHeader('content-disposition', 'attachment; filename=issues_%s.pdf' % self.getId())
        RESPONSE.write(pdf)

    security.declareProtected(View, 'haveReportlab')
    def haveReportlab(self):
        """ check if Reportlab is installed """
        have_rl = getattr(self, '_v_have_rl', None)
        if have_rl is None:
            try:
                import reportlab
                self._v_have_rl = 1
            except ImportError:
                self._v_have_rl = 0
            have_rl = self._v_have_rl
        return have_rl

    security.declareProtected(View, 'haveATReferences')
    def haveATReferences(self):
        """ check for suitable references support in AT (1.3+)"""
        try:
            from Products.Archetypes.config import REFERENCE_CATALOG
            return self.getReferences_mode() == 'enabled'
        except ImportError:
            return 0

    security.declareProtected(View, 'haveUploads')
    def haveUploads(self):
        """ Uploads enabled? """
        return self.getUploads_mode() == 'enabled'

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ hook for 'folder_contents' view """
        return 0

    ######################################################################
    # Issue submission through email
    ######################################################################

    security.declareProtected(EmailSubmission, 'issue_from_xml')
    def issue_from_xml(self, xml, RESPONSE=None):
        """ add issue through xml """
        from xml.dom.minidom import parseString

        def fromDOM(DOM, element):
            l = []
            for node in DOM.getElementsByTagName(element)[0].childNodes:
                if node.nodeType == node.TEXT_NODE:
                    l.append(node.data)
            return ' '.join(l)

        def response(RESPONSE, status, msg):
            if RESPONSE:
                RESPONSE.setStatus(status)
                RESPONSE.write(msg)
            else:
                raise ValueError(msg)

        class record:

            def __init__(self):
                self._k = []

            def set(self, k, v):
                if not k in self._k:
                    self._k.append(k)
                setattr(self, k, v)

            def keys(self):
                return self._k


        DOM = parseString(xml)
        DOM.normalize()

        R = record()
        R.set('title', fromDOM(DOM, 'subject'))
        R.set('description', fromDOM(DOM, 'body'))
        R.set('contact_email', fromDOM(DOM, 'senderaddress'))
        R.set('issue_id', str(fromDOM(DOM, 'issue_id')))

        member = self._member_for_email(R.contact_email)
        if member:
            member_id = member.getUserName()
        else:
            member_id = 'Anonymous User'

        allowed_to_post = self._is_allowed_to_post(member_id)

        if not allowed_to_post:
            msg = 'No permission to post for %s' % str(R.contact_email)
            return response(RESPONSE, 401, msg)

        key = fromDOM(DOM, 'key')
        if key:
            # Followup
            issue_url = self.decode_information(key).strip()
            issue = self.restrictedTraverse(issue_url, None)
            if not issue:
                msg = 'No such issue with URL %s' % issue_url
                return response(RESPONSE, 404, msg)

            issue.getTranscript().add(CommentEvent(R.description, user=member_id))

        elif R.issue_id:
            issue = getattr(self, R.issue_id, None)
            if not issue:
                msg = 'No such issue with id "%s"' % R.issue_id
                return response(RESPONSE, 404, msg)

            comment = R.description + '\n\n' + self.Translate('untrusted_submission', 'Untrusted issue submission: no verification possible')
            issue.getTranscript().add(CommentEvent(comment, user=member_id))

        else:
            # New issue
            id = self.new_issue_number()
            self.invokeFactory('PloneIssueNG', id)
            issue =  self._getOb(id)
            issue.post_creation_actions()
            issue.setParameters(R)
            issue.changeOwnership(member)

            # attachments
            for node in DOM.getElementsByTagName('attachment'):
                cn = node.childNodes[0]
                xmldata = cn.data
                imgdata = base64.decodestring(xmldata)
                issue.upload_file(imgdata,
                                  srcname=node.getAttribute('filename'),
                                  mimetype=node.getAttribute('mimetype'),
                                  notify=0)

            if R.description: 
                issue.getTranscript().add(CommentEvent(R.description, user=member_id))

        issue._last_action = 'Comment'
        issue.reindexObject()
        notifications.notify(issue)
        RESPONSE.write(issue.absolute_url())

    def _member_for_email(self, email):
        """ return the member object for a given email address """

        for member in self.portal_membership.listMembers():
            member_email = member.getProperty('email')
            if member_email:
                if email.lower().strip() == member_email.lower().strip():
                    return member
        return None

    def _is_allowed_to_post(self, userid):
        """ Return 0|1 in case 'userid' is permitted to submit
            submissions through email.
        """

        mode = self.getIssue_email_submission()

        if mode == 'disabled':
            return 0
        elif mode == 'staff':
            user_ids= [u['username'] for u in self.getTrackerUsers(staff_only=1)]
            return userid in user_ids
        elif mode == 'authenticated':
            user_ids= [u['username'] for u in self.getTrackerUsers()]
            return userid in user_ids
        elif mode == 'anyone':
            return 1

    ######################################################################
    # Securitytoken
    ######################################################################

    security.declareProtected(ManageCollector, 'getToken')
    def getToken(self):
        """ return security token"""
        if not hasattr(self, '_token'): self.createToken()
        return self._token

    security.declareProtected(ManageCollector, 'createToken')
    def createToken(self):
        """ create a new token"""
        self._token = md5.new(str(time.time() * random.random())).hexdigest()

    security.declareProtected(View, 'decode_information')
    def decode_information(self, s):
        """ decode a string """

        encrypted = ''
        for i in range(len(s)/2):
            x = s[i*2:i*2+2]
            c = chr(int(x, 16))
            encrypted += c
        orig = util.decrypt(encrypted,self.getToken())
        return orig

    security.declareProtected(View, 'encode_information')
    def encode_information(self, s):
        """ encode a string """

        s = s + (' '*16)[:16-len(s) % 16]
        encrypted_text = util.encrypt(s, self.getToken())
        encoded_text = ''.join(['%02x' % ord(c) for c in encrypted_text])
        return encoded_text

    ######################################################################
    # Misc
    ######################################################################

    def String2DateTime(self, datestr):
        """ Try to convert a date string to a DateTime instance. """

        for fmt in (self.portal_properties.site_properties.localTimeFormat, '%d.%m.%Y', '%d-%m-%Y'):
            try:
                return DateTime('%d/%d/%d' % (time.strptime(datestr, fmt))[:3])
            except ValueError:
                pass

        try:
            return DateTime(datestr)
        except:
            raise ValueError('Unsupported date format: %s' % datestr)

    security.declareProtected(View, 'quote')
    def quote(self, s):
        """ urlquote wrapper """
        return urllib.quote(s)

    ######################################################################
    # Slots handling
    ######################################################################

    def left_slots(self):
        slots_left = list(self.getCollector_portlets_left())
        if 'Plone' in slots_left: 
            slots_left.remove('Plone')
            slots = getattr(self.aq_parent, 'left_slots', [])
            if callable(slots): slots = slots()
            slots = list(slots)
        else:
            slots = []
        slots.extend(slots_left)
        return slots
    left_slots = ComputedAttribute(left_slots, 1)

    def right_slots(self):
        slots_right = list(self.getCollector_portlets_right())
        if 'Plone' in slots_right: 
            slots_right.remove('Plone')
            slots = getattr(self.aq_parent, 'right_slots', [])
            if callable(slots): slots = slots()
            slots = list(slots)
        else:
            slots = []
        slots.extend(slots_right)
        return slots
    right_slots = ComputedAttribute(right_slots, 1)

    def base_edit(self, RESPONSE=None):
        """ redirect to our own edit method """
        if RESPONSE:
            RESPONSE.redirect('pcng_base_edit')

registerType(PloneCollectorNG)


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication','references','metadata', 'edit', 'localroles'):
            a['visible'] = 0
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ['PloneIssueNG', 'Temporary Folder']
    fti['icon'] = 'collector_icon.gif'
    return fti
