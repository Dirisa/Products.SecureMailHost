"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Collector.py,v 1.167 2004/04/24 16:14:19 ajung Exp $
"""

import base64, time, random, md5, os

from Globals import InitializeClass
from Acquisition import aq_base
from AccessControl import  ClassSecurityInfo
from Products.CMFCore.CatalogTool import CatalogTool
from BTrees.OOBTree import OOBTree
from ZODB.POSException import ConflictError
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import OrderedDict
from Base import Base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCorePermissions import *
from Products.PythonScripts.PythonScript import PythonScript

from Transcript import Transcript
from Products.PloneCollectorNG.WorkflowTool import WorkflowTool
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup, EditCollectorIssue, EmailSubmission
from config import CollectorCatalog, SEARCHFORM_IGNOREABLE_INDEXES, CollectorWorkflow
from Issue import PloneIssueNG
from SchemaEditor import SchemaEditor
from Translateable import Translateable
from workflows import VOC_WORKFLOWS
import notifications
import collector_schema 
import issue_schema
import util

class PloneCollectorNG(Base, SchemaEditor, Translateable):
    """ PloneCollectorNG """

    schema = collector_schema.schema
    archetype_name = 'PCNG Tracker'

    actions = ({
        'id': 'pcng_browse',
        'name': 'Browse',
        'action': 'pcng_view',
        'permissions': (View,)
        },
        {'id': 'pcng_configuration',
        'name': 'Configuration',
        'action': 'pcng_configuration',
        'permissions': (ManageCollector,)
        },
        {'id': 'pcng_addissue',
        'name': 'Add issue',
        'action': 'redirect_create_object',
        'permissions': (AddCollectorIssue,)
        },
        {'id': 'pcng_history',
        'name': 'History',
        'action': 'pcng_history',
        'permissions': (ManageCollector,)
        },
        {'id': 'pcng_reports',
        'name': 'Reports',
        'action': 'pcng_reports',
        'permissions': (ManageCollector,)
        },
        )

    __ac_roles__ = ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter')
    security = ClassSecurityInfo()

    def __init__(self, oid, **kwargs):
        Base.__init__(self, oid, **kwargs)
        self.initializeArchetype()
        self.atse_init(issue_schema.schema)   # initialize SchemaEditor 
        self._num_issues = 0
        self._supporters = self._managers = self._reporters = []
        self._notification_emails = OOBTree()

        # setup roles 
        username = util.getUserName()
        for role in ('Manager', 'TrackerAdmin', 'Owner'):
            util.addLocalRole(self, username, role)

    def manage_afterAdd(self, item, container):
        """ post creation (or post renaming) actions """
        Base.manage_afterAdd(self, item, container)

        if getattr(self, '_already_created', 0) == 0:    
            # Upon creation we need to add the transcript
            self._transcript = Transcript()
            self._transcript.addComment(u'Tracker created')
            self._already_created = 1

        else:
            # manager_afterAdd() is also called when the collector is
            # renamed. So we reindex the issues automatically
            self.reindex_issues()

        self.setup_tools()

        # Archestypes uses hardcoded factory-settings for 'immediate_view'
        # that don't not meet our requirements to jump into the 'view' 
        # from the navigation tree instead into 'edit'. So we tweak
        # 'immediate_view' a bit.

        typestool = getToolByName(self, 'portal_types', None)
        ti = typestool.getTypeInfo('PloneIssueNG')
        ti.immediate_view = 'pcng_issue_view'
        ti = typestool.getTypeInfo('PloneCollectorNG')
        ti.immediate_view = 'pcng_view'

        self._transcript.setEncoding(self.getSiteEncoding())
        self.createToken()
        
    def manage_beforeDelete(self, item, container):
        """ Hook for pre-deletion actions """
        self.unindexObject()

    security.declareProtected(ManageCollector, 'setup_tools')
    def setup_tools(self, RESPONSE=None):
        """ setup up required tools """

        self._setup_catalog()
        self._setup_workflow()
        self.getTranscript().addComment(u'Tool setup')

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

        schema = self.Schema()
        field_names = [ f.getName() for f in schema.fields()]
        for name in REQUEST.form.keys():
            if not name in field_names: continue
            new = REQUEST.get(name, None)
            old = self.getField(name).get(self)
            if old:
                if str(old) != str(new): # Archetypes does not use Zope converters
                    self._transcript.addChange(name, old, new)

        # Look&Feel slots handling
        if REQUEST.has_key('slots_mode'):

            def del_slot(o, slot):
                try: delattr(o, slot)
                except: pass

            orig_left = self.aq_parent.left_slots
            orig_right = self.aq_parent.right_slots
            pcng_slot = 'here/pcng_slots/macros/navigation'

            mode = REQUEST['slots_mode'] 
            nav_slot = REQUEST['navigation_slot']

            if nav_slot == 'no':

                if mode == 'plone':
                    del_slot(self, 'left_slots')
                    del_slot(self, 'right_slots')
                elif mode == 'left':
                    del_slot(self, 'left_slots')
                    self.right_slots = []
                elif mode == 'right':
                    self.left_slots = []
                    del_slot(self, 'right_slots')
                else:
                    self.left_slots = self.right_slots = []

            else:
                
                if mode == 'plone':           
                    slots = list(orig_left)
                    slots.append(pcng_slot)
                    self.left_slots =  slots
                    del_slot(self, 'right_slots')
                elif mode == 'left':
                    self.left_slots = [pcng_slot]
                    self.right_slots = []
                elif mode == 'right':
                    self.left_slots = []
                    self.right_slots = [pcng_slot]
                    

    ######################################################################
    # Transcript
    ######################################################################

    security.declareProtected(View, 'getTranscript')
    def getTranscript(self):
        """ return the Transcript instance """
        return self._transcript

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

        l = []
        membership_tool = getToolByName(self, 'portal_membership', None)
        
        staff = self._managers + self._supporters + self._reporters
        names = staff[:]

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

        self._transcript.addIncrementalChange('managers', self._managers, managers)
        self._transcript.addIncrementalChange('supporters', self._supporters, supporters)
        self._transcript.addIncrementalChange('reporters', self._reporters, reporters)

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
        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')
        self.manage_permission(EditCollectorIssue, roles=target_roles, acquire=0)
        self.manage_permission(AddCollectorIssue, roles=target_roles+add_roles, acquire=0)
        self.manage_permission(AddPortalContent, roles=target_roles+add_roles, acquire=0)

        # AddCollectorIssueFollowup 
        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')
        self.manage_permission(AddCollectorIssueFollowup, roles=target_roles+add_roles, acquire=0)

        # ModifyPortalContent
        target_roles = ('Supporter','TrackerAdmin','Manager', 'Owner')
        self.manage_permission(ModifyPortalContent, roles=target_roles+add_roles, acquire=0)

    def _adjust_view_mode(self):
        """Set role privileges according to view mode."""

        target_roles = ('Supporter','TrackerAdmin','Reporter', 'Manager', 'Owner')

        if self.view_mode == 'authenticated':
            target_roles += ('Authenticated', )
        elif self.view_mode == 'anyone':
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

            self._transcript.addChange('notifications', self._notification_emails.get(state, []), emails)
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
        """ create a new issue """
        id = '%s_%f' % (self.Translate('new_issue', 'NewIssue'), time.time() * random.random())
        RESPONSE.redirect(self.absolute_url() + "/createObject?type_name=PloneIssueNG&id=%s" % id)

    security.declareProtected(AddCollectorIssue, 'add_issue')
    def add_issue(self, RESPONSE=None):
        """ create a new issue """
        id = self.new_issue_number()
        self.invokeFactory('PloneIssueNG', id)
        issue = self._getOb(id)
        issue.post_creation_actions()
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

    security.declareProtected(ManageCollector, 'set_topics_user')    
    def set_topics_user(self, d):
        """Set the topics-user mapping. 'd' maps topic ids to a sequence
           of userIds
        """

        self._topic_user = OOBTree()
        for k in d.keys():
            self._topic_user[k] = getattr(d, k)

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
        Base.reindexObject(self)
        self._adjust_view_mode()           # can we hook this somewhere else?
        self._adjust_participation_mode()

    security.declareProtected(ManageCollector, 'reindex_issues')
    def reindex_issues(self, RESPONSE=None):
        """ reindex all issues """

        for issue in self.objectValues('PloneIssueNG'): issue.reindexObject()
        self._transcript.addComment(u'Issues reindexed')
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
        self._transcript.addComment(u'Number of issues reset to 0')
        util.redirect(RESPONSE, 'pcng_maintenance', 
                      self.Translate('number_issues_reseted', 'Issue number reseted to 0'))

    security.declareProtected(ManageCollector, 'update_schema_for_issues')
    def update_schema_for_issues(self, return_to=None, REQUEST=None, RESPONSE=None):
        """ update stored issue schema for all issues """

        schema = self.atse_getSchema()
        for issue in self.objectValues(('PloneIssueNG',)):
            if hasattr(issue, '_v_schema'):
                issue._v_schema = None

        self._transcript.addComment(u'Issue schemas reseted')
        
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

        # PCNGSchema migration
        self.migrate_schema()

        self._transcript.setEncoding(self.getSiteEncoding())
        self._transcript.addComment(u'Collector schema updated')
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
      
        self._transcript.addComment(u'Issue UIDs reregistered')
        util.redirect(RESPONSE, 'pcng_maintenance',
                      self.Translate('uids_recreated', 'UIDs recreated'))


    security.declareProtected(ManageCollector, 'migrate_issue_workflow_histories')
    def migrate_issue_workflow_histories(self, RESPONSE=None):
        """ Migrate workflow histories of all issues to new workflow id """
        for issue in self.objectValues('PloneIssueNG'):
            issue._migrate_workflow_history()
        self._transcript.addComment(u'Issue workflows migrated')
        util.redirect(RESPONSE, 'pcng_maintenance',
                      self.Translate('issue_workflow_histories_migrated', 'Issue workflow histories migrated'))
      

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
            return 1
        except ImportError:
            return 0

    def rename_objects(self, context, old_id, new_id):
        """ rename an object """
        return context.manage_renameObjects([old_id], [new_id])

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

            issue.getTranscript().addComment(R.description, user=member_id)

        elif R.issue_id:
            issue = getattr(self, R.issue_id, None)
            if not issue:
                msg = 'No such issue with id "%s"' % R.issue_id
                return response(RESPONSE, 404, msg)

            comment = R.description + '\n\n' + self.Translate('untrusted_submission', 'Untrusted issue submission: no verification possible')
            issue.getTranscript().addComment(comment, user=member_id)

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
                issue.getTranscript().addComment(R.description, user=member_id)

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


registerType(PloneCollectorNG)

##########################################################################
# Check the availability of TextIndexNG(2)
##########################################################################

try: import Products.TextIndexNG2; txng_version = 2
except ImportError:
    try: import Products.TextIndexNG; txng_version = 1
    except: txng_version = 0


class PloneCollectorNGCatalog(CatalogTool):
    """ catalog for collector issues """

    id = CollectorCatalog
    meta_type = 'PloneCollectorNG Catalog'
    portal_type = 'PloneCollectorNG Catalog'

    def manage_afterAdd(self, container, item):
        """ recreate catalog """

        # We create the indexes and metadata in the manage_afterAdd() hook
        # an *not+ inside the constructor as usually because we need an
        # acquisition context inside enumerateIndexes() to retrieve
        # the issue schema for custom index creation

        self._initIndexes()

    def enumerateIndexes(self):

        if not hasattr(self, 'aq_parent'): return  []   # only through manage_afterAdd()

        custom = [['status', 'FieldIndex'],
                  ['Creator', 'FieldIndex'],
                  ['created', 'DateIndex'],
                  ['last_action', 'DateIndex'],
                  ['SearchableText', 'TextIndex'],
                  ['importance', 'FieldIndex'],
                  ['classification', 'FieldIndex'],
                  ['topic', 'FieldIndex'],
                  ['assigned_to', 'KeywordIndex'],
                  ['progress_deadline', 'FieldIndex'],
                  ['progress_percent_done', 'FieldIndex'],
                  ['getId', 'FieldIndex'],
                  ['numberFollowups', 'FieldIndex'],
                 ]

        # add custom indexes for fields
        custom_keys = [f[0] for f in custom]

        for f in self.aq_parent.atse_getSchema().fields():
            klass = f.__class__.__name__
            widget = f.widget.__class__.__name__
            if getattr(f, 'createindex', 0) == 1 and f.getName() not in custom_keys:
                if klass in ('StringField', 'TextField'):
                    if widget in ('MultiSelectionWidget',):
                        custom.append( [f.getName(), 'FieldIndex'] )
                    else:
                        custom.append( [f.getName(), 'TextIndex'] )
                elif klass in ('DateTimeField', 'IntField', 'FloatField', 'FixedPointField'):
                    custom.append( [f.getName(), 'FieldIndex'] )
                else:
                    pass

        # Replace TextIndexes with TextIndexNG instances if possible
        for i in range(len(custom)):
            k,v = custom[i]
            if v == 'TextIndex':
                if txng_version == 1: custom[i][1] = 'TextIndexNG'
                if txng_version == 2: custom[i][1] = 'TextIndexNG2'

        return  custom

    def manage_afterClone(self, item):
        self.reindex_issues()

    def enumerateColumns( self ):
        """Return field names of data to be cached on query results."""

        if not hasattr(self, 'aq_parent'): return  []  # only through manage_afterAdd()
        
        custom = ('Description', 'Title', 'Creator', 'created', 'modified',
                  'id', 'status', 'topic', 'classification',
                  'importance', 'assigned_to', 'progress_deadline', 
                  'progress_percent_done', 'getId', 'numberFollowups',
                  'last_action'
                  )
        return custom
    
    def searchResults(self, REQUEST=None, **kw):
        """ Bypass searchResults() of the CatalogTool """
        return self._catalog.searchResults(*(REQUEST,), **kw)

    __call__ = searchResults

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication','references','metadata', 'edit', 'localroles'):
            a['visible'] = 0
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ['PloneIssueNG']
    fti['icon'] = 'collector_icon.gif'
    return fti

InitializeClass(PloneCollectorNGCatalog)
