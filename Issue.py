"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Issue.py,v 1.63 2003/11/03 17:17:56 ajung Exp $
"""

import sys, os
from urllib import unquote

from Globals import Persistent, InitializeClass
from AccessControl import  ClassSecurityInfo, Unauthorized
from OFS.content_types import guess_content_type
from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Schema import Schemata
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import OrderedDict

from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName
from Transcript import Transcript
from WatchList import WatchList
from OrderedSchema import OrderedBaseFolder, OrderedSchema
from Translateable import Translateable
import util, notifications


class IssueRelationship(Persistent):
    security = ClassSecurityInfo()
    
    def __init__(self, collector_title, id, issue_url, comment):
        self.collector_title = collector_title
        self.id = id
        self.issue_url = issue_url
        self.comment = comment

    def __hash__(self):
        return self.issue_url

    security.declarePublic('getId')
    def getId(self): return self.id

    security.declarePublic('getURL')
    def getURL(self): return self.issue_url

    security.declarePublic('getComment')
    def getComment(self): return self.comment

    security.declarePublic('getCollectorTitle')
    def getCollectorTitle(self): return self.collector_title

    def __str__(self):
        return '%s: %s' % (self.issue_url, self.comment)

    __repr__ = __str__

InitializeClass(IssueRelationship)


class PloneIssueNG(OrderedBaseFolder, WatchList, Translateable):
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
        {'id': 'pcng_edit',
        'name': 'Edit',
        'action': 'portal_form/pcng_base_edit',
        'permissions': (AddCollectorIssueFollowup,)
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
        self._last_action = 'Created'          # last action from the followup form
        self._transcript = Transcript()
        self._transcript.addComment('Issue created')

    def Schema(self):
        """ Return our schema (through acquisition....uuuuuh). We override
            the Archetypes implementation because the schema for Issue is 
            maintained as attribute of the parent collector instance.
        """
        
        # Schema seems to be called during the construction phase when there is
        # not acquisition context. So we return the schema itself.

        if not hasattr(self, 'aq_parent'): return self.schema

        # Otherwise get the schema from the parent collector through
        # acquisition and assign it to a volatile attribute for performance
        # reasons

        schema = getattr(self, '_v_schema', None)
        if schema is None:
            self._v_schema = self.aq_parent.schema_getWholeSchema()
        return self._v_schema

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
                                                
    def manage_beforeDelete(self, item, container):
        """ Hook for pre-deletion actions """
        self.unindexObject()

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
                raise Unauthorized(self.translate('invalid_action', 
                                                  'Invalid action: %(action)s', action=action))

            old_status = self.status()
            wf = getToolByName(self, 'portal_workflow')
            wf.doActionFor(self, action,
                           comment=comment,
                           username=util.getUserName(),
                           assignees=assignees)
            new_status = self.status()
            self._transcript.addChange('status', old_status, new_status)

        self._transcript.addAction(action)
        self.notifyModified() # notify DublinCore
        self._last_action = action
        notifications.notify(self)
        util.redirect(RESPONSE, 'pcng_issue_view', 
                      self.translate('followup_submitted', 'Followup submitted'))

    security.declareProtected(CMFCorePermissions.View, 'lastAction')
    def lastAction(self):
        """ return the latest action done """
        return self._last_action

    ######################################################################
    # Archetypes callbacks 
    ######################################################################

    security.declareProtected(AddCollectorIssue, 'setParameters')
    def setParameters(self, parameters):
        """ Takes the 'parameters' record object and update the issue fields.
            (Used for TTW creation of issues)
        """

        for k in parameters.keys():
            if  k in ('id',):
                raise ValueError(self.translate('wrong_parameter', 'The parameter "$id" can not be set', id=k))
            v = getattr(parameters, k)
            field = self.Schema()[k]
            field.storage.set(k, self, v)

    def getParameter(self, key):
        """ return the value of an Archetypes field """

        field = self.Schema()[key]
        return field.storage.get(key, self)

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

    def delete_reference(self, issue_url, RESPONSE=None):
        """ delete a reference given by its position """

        issue = self.getPhysicalRoot().restrictedTraverse(issue_url)
        self.deleteReference(issue)
        util.redirect(RESPONSE, 'pcng_issue_references', 
                      self.translate('reference_deleted', 'Reference has been deleted'))

    def add_reference(self, reference, RESPONSE=None):
        """ add a new reference (record object) """

        tracker_url = unquote(reference.tracker)
        tracker = self.getPhysicalRoot().restrictedTraverse(tracker_url)
        if not tracker:
            raise ValueError(self.translate('no_tracker', 'Tracker does not exist: $tracker_url', tracker_url=tracker_url))

        if getattr(tracker.aq_base, str(reference.ticketnumber), None) is None:
            raise ValueError(self.translate('no_ticket', 'Ticket number does not exist: $ticketnum', ticketnum=reference.ticketnumber))
        issue = tracker[reference.ticketnumber]

        if not reference.comment:
            raise ValueError(self.translate('reference_no_comment', 'References must have a comment'))

        self.addReference(issue, IssueRelationship(tracker.title_or_id(), 
                                                   issue.getId(),
                                                   issue.absolute_url(), 
                                                   reference.comment))
        util.redirect(RESPONSE, 'pcng_issue_references', 
                      self.translate('reference_stored', 'Reference has been stored'))

    security.declareProtected(CMFCorePermissions.View, 'references_tree')
    def references_tree(self, format='gif', RESPONSE=None):
        """ create graphical representation of the references tree
            (using Graphviz) 
        """
        from Products.PloneCollectorNG import graphviz
        graphs, nodes, edges = graphviz.build_tree(self, {}, [], [])
        vizfile = graphviz.build_graphviz(graphs, nodes, edges)
        
        if format in ('gif','jpeg', 'png', 'mif', 'svg', 'ps'):
            graphviz.viz2image(vizfile, format, RESPONSE)
        elif format in ('cmap',):
            graphviz.viz2map(vizfile, format, RESPONSE)
        else:
            raise RuntimeError(self.translate('unknown_format', 'unknown format "$format"', format=format))

    ######################################################################
    # File uploads 
    ######################################################################

    def upload_file(self, uploaded_file=None, comment='', RESPONSE=None):
        """ Upload a file """

        if uploaded_file:
            file_id = uploaded_file.filename.split('/')[-1].split('\\')[-1]
            ct = guess_content_type(file_id, uploaded_file.read())
            if ct[0].find('image') > -1:
                self.invokeFactory('Image', file_id)
            else:
                self.invokeFactory('File', file_id)

            obj = self._getOb(file_id)
            obj.manage_permission(CMFCorePermissions.View, acquire=1)
            obj.manage_permission(CMFCorePermissions.AccessContentsInformation, acquire=1)
            obj.manage_upload(uploaded_file)
            self._transcript.addUpload(file_id, comment)

            self._last_action = 'Upload'
            notifications.notify(self)

            util.redirect(RESPONSE, 'pcng_issue_references', 
                          self.translate('file_uploaded', 'File base been uploaded'))
        else:
            util.redirect(RESPONSE, 'pcng_issue_references', 
                          self.translate('nothing_for_upload', 'Nothing to be uploaded'))

    security.declareProtected(ManageCollector, 'upload_remove')
    def upload_remove(self, id, RESPONSE):
        """ Remove an uploaded file """
        self.manage_delObjects([id])
        util.redirect(RESPONSE, 'pcng_issue_references', 
                     self.translate('upload_removed', 'File has been removed'))


    ######################################################################
    # Misc
    ######################################################################

    security.declareProtected(CMFCorePermissions.View, '_getCollector')
    def _getCollector(self):
        """ return collector instance """
        return self.aq_parent

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
        return len(self._transcript.getEventsGrouped())

    ######################################################################
    # Catalog stuff
    ######################################################################

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=None):
        """ reindex issue """
        catalogs = [getattr(self, 'pcng_catalog'), getToolByName(self, 'portal_catalog', None)]
        for c in catalogs: c.indexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        catalogs = [getattr(self, 'pcng_catalog'), getToolByName(self, 'portal_catalog', None)]
        for c in catalogs: c.unindexObject(self)
                
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
        if a['id'] in ('syndication','references','metadata', 'edit'):
            a['visible'] = 0

    fti['global_allow'] = 0
    return fti

registerType(PloneIssueNG)
