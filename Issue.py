"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: Issue.py,v 1.111 2004/01/12 20:13:08 ajung Exp $
"""

import sys, os, time
from urllib import unquote

from Globals import Persistent, InitializeClass
from AccessControl import  ClassSecurityInfo, Unauthorized
from OFS.content_types import guess_content_type
from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.CMFCorePermissions import *
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Schema import Schema
from Products.Archetypes.public import registerType
from Products.Archetypes.utils import OrderedDict
from Products.Archetypes.config import TOOL_NAME as ARCHETOOL_NAME
from zLOG import LOG, ERROR

from Base import Base, ParentManagedSchema
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName, CollectorCatalog
from Transcript import Transcript
from WatchList import WatchList
from Translateable import Translateable
import util, notifications


_marker = []

class PloneIssueNG(ParentManagedSchema, Base, WatchList, Translateable):
    """ PloneCollectorNG """

    actions = ({
        'id': 'pcng_browse',
        'name': 'Browse',
        'action': 'pcng_ticket_browser',
        'permissions': (View,)
        },
        {'id': 'pcng_issue_view',
        'name': 'View',
        'action': 'pcng_issue_view',
        'permissions': (View,)
        },
        {'id': 'followup',
        'name': 'Followup',
        'action': 'pcng_issue_followup',
        'permissions': (AddCollectorIssueFollowup,)
        },
        {'id': 'pcng_edit',
        'name': 'Edit',
        'action': 'pcng_base_edit',
        'permissions': (ModifyPortalContent,)
        },
        {'id': 'issue_references',
        'name': 'References & Uploads',
        'action': 'pcng_issue_references',
        'permissions': (AddCollectorIssueFollowup,)
        },
        {'id': 'issue_add_issue',
        'name': 'Add issue',
        'action': 'add_issue',
        'permissions': (AddCollectorIssue,)
        },
        {'id': 'issue_debug',
        'name': 'Debug',
        'action': 'pcng_issue_debug',
        'permissions': (ManageCollector,)
        },
        )

    security = ClassSecurityInfo()

    def __init__(self, id):
        Base.__init__(self, id) 
        from issue_schema import schema
        self.schema = schema
        self.wl_init()
        self.id = id
        self.title = id
        self._last_action = 'Created'          # last action from the followup form
        self._transcript = Transcript()

    def manage_afterAdd(self, item, container):
        """ perform post-creation actions """

        Base.manage_afterAdd(self, item, container)

        # added member preferences as defaults to the issue
        member = getToolByName(self, 'portal_membership', None).getMemberById(util.getUserName())
        schema = self.Schema()

        if member:
            fieldnames = [ f.getName() for f in schema.fields() ]
            for name, name1 in ( ('contact_name', 'fullname'), ('contact_email', 'email'), \
                                ('contact_company', 'pcng_company'), ('contact_position', 'pcng_position'),
                                ('contact_address', 'pcng_address'), ('contact_fax', 'pcng_fax'), \
                                ('contact_phone', 'pcng_phone'), ('contact_city', 'pcng_city')):

                if name in fieldnames:                
                    schema[name].set(self, member.getProperty(name1))
        else:
            name = 'contact_name'
            schema[name].set(self, util.getUserName())

        # pre-allocate the deadline property
        self.progress_deadline = DateTime() + self.deadline_tickets        

        # notify workflow and index issue
        if aq_base(container) is not aq_base(self):
            wf = getToolByName(self, 'portal_workflow')
            wf.notifyCreated(self)

        self.initializeArchetype()
                                                
    def manage_beforeDelete(self, item, container):
        """ Hook for pre-deletion actions """
        self.unindexObject()

    ######################################################################
    # Followups
    ######################################################################

    def issue_followup(self, action, comment='', text_format='plain', assignees=[], RESPONSE=None):
        """ issue followup handling """

        # action for changes in assignment
        old_assignees = self.assigned_to()
        assignees_changed = 0
        if not util.lists_eq(assignees, old_assignees):
            self._transcript.addChange('assignees', old_assignees, assignees)
            assignees_changed = 1

        if comment: self._transcript.addComment(unicode(comment, self.getSiteEncoding()), text_format)  
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

    security.declareProtected(View, 'lastAction')
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

        schema = self.Schema()
        for k in parameters.keys():
            if  k in ('id',):
                raise ValueError(self.translate('wrong_parameter', 'The parameter "$id" can not be set', id=k))
            v = getattr(parameters, k)
            field = schema[k]
            field.set(self, v)

    def getParameter(self, key):
        """ return the value of an Archetypes field """

        field = self.Schema()[key]
        try: return field.get(self)  # avoid problems with updated schemas
        except: return ''

    ######################################################################
    # Transcript
    ######################################################################

    security.declareProtected(View, 'getTranscript')
    def getTranscript(self):
        """ return the Transcript instance """
        return self._transcript

    ######################################################################
    # References handling
    ######################################################################

    security.declareProtected(ManageCollector, 'delete_reference')
    def delete_reference(self, issue_url, RESPONSE=None):
        """ delete a reference given by its position """

        issue = self.getPhysicalRoot().restrictedTraverse(issue_url)
        self.deleteReference(issue)
        util.redirect(RESPONSE, 'pcng_issue_references', 
                      self.translate('reference_deleted', 'Reference has been deleted'))

    security.declareProtected(AddCollectorIssueFollowup, 'add_reference')
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

        self.addReference(issue, "relates_to", issue_id=issue.getId(),
                                               issue_url=issue.absolute_url(1), 
                                               collector_title=tracker.getId(),
                                               comment=reference.comment)

        util.redirect(RESPONSE, 'pcng_issue_references', 
                      self.translate('reference_stored', 'Reference has been stored'))


    security.declareProtected(View, 'getForwardReferences')
    def getForwardReferences(self):
        """ AT forward references """
        from Products.Archetypes.config import REFERENCE_CATALOG
        tool = getToolByName(self, REFERENCE_CATALOG)
        refs = tool.getReferences(self, None)
        return refs
        
    security.declareProtected(View, 'getBackReferences')
    def getBackReferences(self):
        """ AT forward references """
        from Products.Archetypes.config import REFERENCE_CATALOG
        tool = getToolByName(self, REFERENCE_CATALOG)
        sID, sobj = tool._uidFor(self)
        brains = tool._queryFor(tid=sID, relationship=None)
        refs = tool._resolveBrains(brains)
        return refs
        
    security.declareProtected(View, 'references_tree')
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

    security.declareProtected(AddCollectorIssueFollowup, 'upload_file')
    def upload_file(self, uploaded_file=None, comment='', RESPONSE=None):
        """ Upload a file """

        if uploaded_file:
            file_id = uploaded_file.filename.split('/')[-1].split('\\')[-1]
            ct = guess_content_type(file_id, uploaded_file.read())
            if file_id in self.objectIds():
                name,ext = os.path.splitext(file_id)
                file_id = '%s_%s%s' % (name, time.strftime('%Y%m%d_%H%M%S', time.localtime()), ext)

            if ct[0].find('image') > -1:
                self.invokeFactory('Image', file_id)
            else:
                self.invokeFactory('File', file_id)

            obj = self._getOb(file_id)
            if comment: obj.title = comment
            obj.manage_permission(View, acquire=1)
            obj.manage_permission(AccessContentsInformation, acquire=1)
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

    security.declareProtected(View, '_getCollector')
    def _getCollector(self):
        """ return collector instance """
        parent = self.aq_parent
        while 1:
            if parent.meta_type != 'PloneCollectorNG':
                parent = parent.aq_parent
            else: 
                break
        return parent

    def pre_validate(self, REQUEST, errors):
        """ Hook to perform pre-validation actions. We use this
            hook to log changed properties to the transcript.
        """
        schema = self.Schema()
        field_names = [ f.getName() for f in schema.fields()]
        for name in REQUEST.form.keys():
            if not name in field_names: continue
            new = REQUEST.get(name, None)
            old = schema[name].get(self)
            self._transcript.addChange(name, old, new)

    def post_validate(self, REQUEST, errors):
        """ Hook to perform post-validation actions. We use this
            to reindex the issue.
        """
        self.notifyModified() # notify DublinCore

    def __len__(self):
        """ return the number of transcript events """
        return len(self._transcript.getEventsGrouped())
    numberFollowups = __len__

    def pcng_ticket_browser(self, RESPONSE=None):
        """ redirect to ticket browser """
        util.redirect(RESPONSE, self.aq_parent.absolute_url() + '/pcng_view')

    def view(self, REQUEST=None, RESPONSE=None):
        """ override 'view' """
        return self.pcng_issue_view(REQUEST=REQUEST, RESPONSE=RESPONSE)

    base_view = view

    ######################################################################
    # Catalog stuff
    # 
    # In V 1.0 and below we used to reindex the issue with the collector
    # catalog and the portal catalog. Starting V 1.0.1 we use only the
    # portal catalog until we have ifixedthe problem with the migration code
    # in Field.set() of AT that does not work with DublicCore fields that
    # not defined on the issue schema. Maybe in the future this change
    # might be reverted
    ######################################################################


    def _get_catalog(self):
        """ return collector catalog """
        return getattr(self, CollectorCatalog)

    def _get_archetypes_catalogs(self):
        """ return catalogs that are maintainted by Archetypes """

        at = getToolByName(self, ARCHETOOL_NAME , None)
        catalogs = at.getCatalogsByType(self.meta_type) or []
        catalogs = [c for c in catalogs if c.getId() not in ('portal_catalog', )]
        if not catalogs:
            LOG('plonecollectorng', ERROR, 'getCatalogsByType() returned no usable catalogs') 
        return catalogs

    security.declareProtected(ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=None):
        """ reindex issue """

        self._get_catalog().indexObject(self)  # reindex with collector catalog

        for c in self._get_archetypes_catalogs():
            c.catalog_object(self, '/'.join(self.getPhysicalPath()))

    security.declareProtected(ModifyPortalContent, 'unindexObject')
    def unindexObject(self):

        self._get_catalog().unindexObject(self)  # reindex with collector catalog

        for c in self._get_archetypes_catalogs():
            c.uncatalog_object('/'.join(self.getPhysicalPath()))
                
    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        """ return all indexable texts """

        l = []
        l.extend(self.objectIds())
        l.extend([o.title_or_id() for o in self.objectValues()])
        for field in self.Schema().fields():
            v = field.get(self)
            if v:
                if callable(v): v = v()
                l.append( str(v) )
        return ' '.join(l)

    ######################################################################
    # Callbacks for parent collector instance
    ######################################################################

    security.declareProtected(AddCollectorIssue, 'add_issue')
    def add_issue(self, RESPONSE):
        """ redirect to parent """
        return self._getCollector().add_issue(RESPONSE=RESPONSE)

    ######################################################################
    # Presentation related stuff
    ######################################################################

    security.declareProtected(View, 'title_or_id')
    def title_or_id(self):
        """ return the id + title (override for navigation tree) """
        return '%s: %s' %  (self.getId(), self.Title())

    security.declareProtected(View, 'asPDF')
    def asPDF(self, RESPONSE):
        """ Produce a PDF for issue"""
        import pdfwriter

        pdf = pdfwriter.pdfwriter(self.aq_parent, [self.getId()]) 
        RESPONSE.setHeader('content-type', 'application/pdf')
        RESPONSE.setHeader('content-length', str(len(pdf)))
        RESPONSE.setHeader('content-disposition', 'attachment; filename=issue_%s_%s.pdf' % (self.aq_parent.getId(), self.getId()))
        RESPONSE.write(pdf)

    ######################################################################
    # Callbacks for pcng_issue_workflow
    ######################################################################

    security.declareProtected(View, 'assigned_to')
    def assigned_to(self, sorted=0):
        """ return assigned users according to the workflow """
        wftool = getToolByName(self, 'portal_workflow')
        users = list(wftool.getInfoFor(self, 'assigned_to', ()) or ())
        if sorted: users.sort()
        return users

    security.declareProtected(View, 'is_assigned')
    def is_assigned(self):
        """ return if the current is user among the assignees """
        username = util.getUserName()
        return username in self.assigned_to()

    security.declareProtected(View, 'is_confidential')
    def is_confidential(self):
        """ return if the issue is confidential according to the workflow """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'confidential', 0)

    security.declareProtected(View, 'status')
    def status(self):
        """ return workflow state """
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'state', 'pending')

    security.declareProtected(View, 'validActions')
    def validActions(self):
        """ return valid transitions for issue 'pcng_issue_workflow' """
        pa = getToolByName(self, 'portal_actions', None)
        allactions = pa.listFilteredActionsFor(self)
        return [entry['name'] for entry in allactions.get(IssueWorkflowName, [])]

    security.declareProtected(View, 'getWorkflowHistory')
    def getWorkflowHistory(self):                     
        """ return the workflow history """
        return self.workflow_history[IssueWorkflowName]


    ######################################################################
    # Override processForm() from Archetype.BaseObject
    ######################################################################

    security.declarePrivate('_processForm')
    def _processForm(self, data=1, metadata=None, REQUEST=None,values=None):

        request = REQUEST or self.REQUEST
        schema = self.Schema()

        for k in request.form.keys():
            if not schema.has_key(k): continue
            field = schema[k]

            widget = field.widget
            result = widget.process_form(self, field, request.form, empty_marker=_marker)
            if result is _marker or result is None: continue

            # Set things by calling the mutator
            mutator = field.getMutator(self)
            __traceback_info__ = (self, field, mutator)
            mutator(result[0], **result[1])

        self.reindexObject()

registerType(PloneIssueNG)

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ('view', 'syndication','references','metadata', 'edit'):
            a['visible'] = 0

    fti['global_allow'] = 0
    fti['filter_content_types'] = 1
    fti['allowed_content_types'] = ['File', 'Portal File', 'Image', 'Portal Image']
    return fti

