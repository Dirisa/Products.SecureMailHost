"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Issue.py,v 1.32 2003/09/30 11:16:26 ajung Exp $
"""

import sys, os
from urllib import unquote

from AccessControl import  ClassSecurityInfo, Unauthorized
from Acquisition import aq_base
from DateTime import DateTime
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
        self._references = ReferencesManager()
        self._transcript = Transcript()
        self._transcript.addComment('Issue created')

    def manage_afterAdd(self, item, container):
        """ perform post-creation actions """
        OrderedBaseFolder.manage_afterAdd(self, item, container)

        # added member preferences as defaults to the issue
        member = getToolByName(self, 'portal_membership', None).getMemberById(util.getUserName())

        if member:
            fieldnames = [ f.getName() for f in self.Schema().fields() ]
            for name, name1 in ( ('contact_name', 'fullname'), ('contact_email', 'email'), \
                                ('contact_company', 'pcng_company'), ('contact_position', 'pcng_position'),
                                ('contact_address', 'pcng_address'), ('contact_fax', 'pcng_fax'), \
                                ('contact_phone', 'pcng_phone'), ('contact_city', 'pcng_city')):

                if name in fieldnames:                
                    self.Schema()[name].storage.set(name, self, member.getProperty(name1))
        else:
            name = 'contact_name'
            self.Schema()[name].storage.set(name, self, util.getUserName())

        # pre-allocate the deadline property
        self.progress_deadline = DateTime() + self.deadline_tickets        

        # notify workflow and index issue
        if aq_base(container) is not aq_base(self):
            wf = getToolByName(self, 'portal_workflow')
            wf.notifyCreated(self)
                                                
    ######################################################################
    # Followups
    ######################################################################

    def issue_followup(self, action, comment='', assignees=[], RESPONSE=None):
        """ issue followup handling """

        # action for changes in assignment
        old_assignees = self.assigned_to()
        assignees_changed = 0
        if not util.lists_eq(assignees, old_assignees):
            self._transcript.addChange('assignees', old_assignees, assignees)
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

        tracker_url = unquote(reference.tracker)

        if not reference.comment:
            raise ValueError('References must have a comment')

        tracker = self.restrictedTraverse(tracker_url)
        if not tracker:
            raise ValueError('Tracker does not exist: %s' % tracker_url)

        if getattr(tracker.aq_base, str(reference.ticketnumber), None) is None:
            raise ValueError('Ticket number does not exist: %s' % reference.ticketnumber)

        ref = Reference(tracker_url, reference.ticketnumber, reference.comment)
        self._references.add(ref)
        self._transcript.addReference(tracker_url, reference.ticketnumber, reference.comment)

        util.redirect(RESPONSE, 'pcng_issue_references', 'Reference has been stored')

    security.declareProtected(CMFCorePermissions.View, 'references_tree')
    def references_tree(self, format='gif', RESPONSE=None):
        """ create graphical representation of the references tree
            (using Graphviz) 
        """
        from Products.PloneCollectorNG import references

        graphs, nodes, edges = references.build_tree(self, {}, [], [])
        vizfile = references.build_graphviz(graphs, nodes, edges)
        
        if format in ('gif','jpeg', 'png', 'mif', 'svg', 'ps'):
            references.viz2image(vizfile, format, RESPONSE)
        elif format in ('cmap',):
            references.viz2map(vizfile, format, RESPONSE)
        else:
            raise RuntimeError('unknown format "%s"' % format)

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

    def __len__(self):
        """ return the number of transcript events """
        return len(self._transcript)

    ######################################################################
    # Catalog stuff
    ######################################################################

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=None):
        """ reindex issue """
        catalogs = [getattr(self, 'pcng_catalog'), getToolByName(self, 'portal_catalog', None)]
        for c in catalogs: c.indexObject(self)

    def SearchableText(self):
        """ return all indexable texts """

        l = []
        for field in self.Schema().fields():
        
            v = getattr(self, field.getName(), None)
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
    # Presentation related stuff
    ######################################################################

    def title_or_id(self):
        """ return the id + title (override for navigation tree) """
        return '%s: %s' %  (self.getId(), self.Title())

    ######################################################################
    # Callbacks for pcng_issue_workflow
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, 'assigned_to')
    def assigned_to(self, sorted=0):
        """ return assigned users according to the workflow """
        wftool = getToolByName(self, 'portal_workflow')
        users = list(wftool.getInfoFor(self, 'assigned_to', ()) or ())
        if sorted: users.sort()
        return users

    security.declareProtected(CMFCorePermissions.View, 'is_assigned')
    def is_assigned(self):
        """ return if the current is user among the assignees """
        username = util.getUserName()
        return username in self.assigned_to()

    security.declareProtected(CMFCorePermissions.View, 'is_confidential')
    def is_confidential(self):
        """ return if the issue is confidential according to the workflow """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'confidential', 0)

    security.declareProtected(CMFCorePermissions.View, 'status')
    def status(self):
        """ return workflow state """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'state', 'pending')

    security.declareProtected(CMFCorePermissions.View, 'validActions')
    def validActions(self):
        """ return valid transitions for issue 'pcng_issue_workflow' """
        pa = getToolByName(self, 'portal_actions', None)
        allactions = pa.listFilteredActionsFor(self)
        return [entry['name'] for entry in allactions.get(IssueWorkflowName, [])]

    security.declareProtected(CMFCorePermissions.View, 'getWorkflowHistory')
    def getWorkflowHistory(self):
        """ return the workflow history """
        return self.workflow_history[IssueWorkflowName]

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('syndication','references','metadata'):
            a['visible'] = 0
    return fti

registerType(PloneIssueNG)
