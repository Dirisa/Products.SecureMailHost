"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Issue.py,v 1.21 2003/09/21 11:22:50 ajung Exp $
"""

import sys

from AccessControl import  ClassSecurityInfo, Unauthorized
from Acquisition import aq_base
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import OrderedDict

from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName
from Transcript import Transcript
from References import Reference, ReferencesManager
from WatchList import WatchList
from OrderedSchema import OrderedBaseFolder, OrderedSchema
import util

class PloneIssueNG(OrderedBaseFolder, WatchList):
    """ PloneCollectorNG """

    actions = ({
        'id': 'view',
        'name': 'View',
        'action': 'pcng_issue_view',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'followup',
        'name': 'Followup',
        'action': 'pcng_issue_followup',
        'permissions': (AddCollectorIssueFollowup,)
        },
#        {'id': 'edit',
#        'name': 'Edit',
#        'action': 'pcng_base_edit',
#        'permissions': (AddCollectorIssueFollowup,)
#        },
        {'id': 'history',
        'name': 'History',
        'action': 'pcng_issue_history',
        'permissions': (CMFCorePermissions.View,)
        },
        {'id': 'issue_references',
        'name': 'References & Uploads',
        'action': 'pcng_issue_references',
        'permissions': (AddCollectorIssueFollowup,)
        },
        {'id': 'issue_add_issue',
        'name': 'Add Issue',
        'action': 'add_issue',
        'permissions': (AddCollectorIssue,)
        },
        {'id': 'issue_debug',
        'name': 'Debug',
        'action': 'pcng_issue_debug',
        'permissions': (AddCollectorIssue,)
        },
        )

    security = ClassSecurityInfo()

    def __init__(self, id, title, schema, **kw):
        self.schema = schema
        OrderedBaseFolder.__init__(self, id, **kw)
        self.initializeArchetype()
        self.wl_init()
        self.id = id
        self.title = title 
        self.security_related = 0
        self._assignees = []
        self._references = ReferencesManager()
        self._transcript = Transcript()
        self._transcript.addComment('Issue created')

    def manage_afterAdd(self, item, container):
        """ perform post-creation actions """
        OrderedBaseFolder.manage_afterAdd(self, item, container)

        # add email/fullname to the contact properties of the issue
        member = getToolByName(self, 'portal_membership', None).getMemberById(util.getUserName())
        if member:
            name = 'contact_name'
            self.Schema()[name].storage.set(name, self, member.getProperty('fullname'))
            name = 'contact_email'
            self.Schema()[name].storage.set(name, self, member.getProperty('email'))
        else:
            name = 'contact_name'
            self.Schema()[name].storage.set(name, self, util.getUserName())

        # notify workflow and index issue
        if aq_base(container) is not aq_base(self):
            wf = getToolByName(self, 'portal_workflow')
            wf.notifyCreated(self)
            self.indexObject()
                                                
    ######################################################################
    # Followups
    ######################################################################

    def issue_followup(self, action, comment='', assignees=[], RESPONSE=None):
        """ issue followup handling """

        # action for changes in assignment
        assignees_changed = 0
        if not util.lists_eq(assignees, self._assignees):
            self._transcript.addChange('assignees', self._assignees, assignees)
            self._assignees = assignees 
            assignees_changed = 1

        if comment: self._transcript.addComment(comment)  
        if action == 'comment' and assignees_changed: action = 'assign'

        # perform workflow action
        if not action in ('comment', ):

            if action != 'request' and not action in self.validActions():
                raise Unauthorized('Invalid action: %s' % action)

            old_status = self.status()
            wf = getToolByName(self, 'portal_workflow')
            wf.doActionFor(self, action,
                           comment=comment,
                           username=util.getUserName(),
                           assignees=assignees)
            new_status = self.status()
            self._transcript.addChange('status', old_status, new_status)

        self.notifyModified() # notify DublinCore
        self.indexObject()
        util.redirect(RESPONSE, 'pcng_issue_view', 'Followup submitted')

    ######################################################################
    # Archetypes callbacks 
    ######################################################################

    def archetypes_mutator(self, v, **kw):
        """ the Archetypes mutator callback.
            ATT: we pass the Field instance as kw-arg 'field'
            This requires a hacked Archetypes.BaseObject.py (lines 366ff)
        """
        field = sys._getframe().f_back.f_locals['field']
        field.storage.set(field.getName(), self, v, **kw)

    def archetypes_accessor(self, *args, **kw):
        """ this method is a very bad hack since we do intercept
            the frame to get hold of the corresponding 'field' object
        """

        # look for the context in the stack
        _marker = []
        frame = sys._getframe()
        context = _marker
        while context is _marker and frame is not None:
            context = frame.f_locals.get('econtext', _marker)
            frame = frame.f_back
        if context is _marker:
            return None

        field = context.local_vars['field']
        try:
            value = field.storage.get(field.getName(), self, **kw)
        except:
            value = None
        return value 

    ######################################################################
    # Transcript
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'getTranscript')
    def getTranscript(self):
        """ return the Transcript instance """
        return self._transcript

    ######################################################################
    # References handling
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'getReferences')
    def getReferences(self):
        """ return a sequences of references """
        return self._references

    def add_reference(self, reference, RESPONSE=None):
        """ add a new reference (record object) """

        if not reference.comment:
            raise ValueError('References must have a comment')

        tracker = self.restrictedTraverse(reference.tracker)
        if not tracker:
            raise ValueError('Tracker does not exist: %s' % reference.tracker)

        if getattr(tracker.aq_base, str(reference.ticketnumber), None) is None:
            raise ValueError('Ticket number does not exist: %s' % reference.ticketnumber)

        ref = Reference(reference.tracker, reference.ticketnumber, reference.comment)
        self._references.add(ref)
        self._transcript.addReference(reference.tracker, reference.ticketnumber, reference.comment)

        util.redirect(RESPONSE, 'pcng_issue_references', 'Reference has been stored')

    ######################################################################
    # File uploads 
    ######################################################################

    def upload_file(self, uploaded_file=None, comment='', RESPONSE=None):
        """ Upload a file """

        if uploaded_file:
            file_id = uploaded_file.filename
            file_id = file_id.split('/')[-1].split('\\')[-1]
            self.invokeFactory('File', file_id)
            obj = self._getOb(file_id)
            obj.manage_permission(CMFCorePermissions.View, acquire=1)
            obj.manage_permission(CMFCorePermissions.AccessContentsInformation, acquire=1)
            obj.manage_upload(uploaded_file)
            self._transcript.addUpload(file_id, comment)

            util.redirect(RESPONSE, 'pcng_issue_references', 'File base been uploaded')
        else:
            util.redirect(RESPONSE, 'pcng_issue_references', 'Nothing to be uploaded')

    ######################################################################
    # Misc
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'getAssignees')
    def getAssignees(self):
        """ return list of assigned usernames """
        return self._assignees

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """

        field_names = [ f.getName() for f in self.Schema().fields()]
        for name in REQUEST.form.keys():
            if not name in field_names: continue
            new = REQUEST.get(name, None)
            old = getattr(self, name, '')
            self._transcript.addChange(name, old, new)

    def post_validate(self, REQUEST, errors):
        """ Hook to perform post-validation actions. We use this
            to reindex the issue.
        """
        self.notifyModified() # notify DublinCore
        self.indexObject()

    def __len__(self):
        """ return the number of transcript events """
        return len(self._transcript)

    ######################################################################
    # Catalog stuff
    ######################################################################

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'reindexObject')
    def indexObject(self):
        catalogs = [getattr(self, 'pcng_catalog'), getToolByName(self, 'portal_catalog', None)]
        for c in catalogs: c.indexObject(self)

    def SearchableText(self):
        """ return all indexable texts """

        l = []
        for attr in ('title' ,'description' ,'solution' ,'topic' ,'subtopic',
                     'classification' ,'importance' ,'status' ,'version_info',
                     'contact_name' ,'contact_city' ,'contact_fax',
                     'contact_phone' ,'contact_address' ,'contact_email'):

            v = getattr(self, attr, None)
            if v:
                if callable(v): v = v()
                l.append( str(v) )

        return ' '.join(l)

    ######################################################################
    # Callbacks for parent collector instance
    ######################################################################

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'updateSchema')
    def updateSchema(self, schema):
        """ Update the schema. Called from the PloneCollectorNG instance
            to update all schemas of all childs since the schema is an
            instance attribute and not a class attribute.
        """
        self.schema = schema

    def add_issue(self, RESPONSE):
        """ redirect to parent """
        return self.aq_parent.add_issue(RESPONSE=RESPONSE)

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

    ######################################################################
    # Callbacks for pcng_issue_workflow
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'assigned_to')
    def assigned_to(self, sorted=0):
        """ return assigned users according to the workflow """
        wftool = getToolByName(self, 'portal_workflow')
        users = wftool.getInfoFor(self, 'assigned_to', ())or ()
        if sorted:
            users = list(users); users.sort()
        return users

    security.declareProtected(CMFCorePermissions.View, 'is_assigned')
    def is_assigned(self):
        """ return if the current is user among the assignees """
        username = util.getUserName()
        return username in self._assignees

    security.declareProtected(CMFCorePermissions.View, 'is_confidential')
    def is_confidential(self):
        """ return if the issue is confidential according to the workflow """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'confidential', 0)

    security.declareProtected(CMFCorePermissions.View, 'status')
    def status(self):
        """ return workflow state """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'state', 'Pending')

    security.declareProtected(CMFCorePermissions.View, 'validActions')
    def validActions(self):
        """ return valid transitions for issue 'pcng_issue_workflow' """
        pa = getToolByName(self, 'portal_actions', None)
        allactions = pa.listFilteredActionsFor(self)
        return [entry['name'] for entry in allactions.get(IssueWorkflowName, [])]

    security.declareProtected(CMFCorePermissions.View, 'getWorkflowHistory')
    def getWorkflowHistory(self):
        """ return the workflow history """
        return self.workflow_history['pcng_issue_workflow']

registerType(PloneIssueNG)
