"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Issue.py,v 1.12 2003/09/10 13:46:52 ajung Exp $
"""

import sys

from AccessControl import  ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import BaseFolder, registerType

from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName
from Transcript import Transcript, TranscriptEntry
from References import Reference, ReferencesManager
from WatchList import WatchList
import util

class PloneIssueNG(BaseFolder, WatchList):
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
        {'id': 'history',
        'name': 'History',
        'action': 'pcng_issue_history',
        'permissions': (AddCollectorIssue,)
        },
        {'id': 'issue_references',
        'name': 'References & Uploads',
        'action': 'pcng_issue_references',
        'permissions': (AddCollectorIssue,)
        },
        {'id': 'issue_add_issue',
        'name': 'Add Issue',
        'action': 'add_issue',
        'permissions': (AddCollectorIssue,)
        },
        )

    security = ClassSecurityInfo()

    def __init__(self, id, title, schema, **kw):
        self.schema = schema
        BaseFolder.__init__(self, id, **kw)
        self.initializeArchetype()
        self.wl_init()
        self.id = id
        self.title = title 
        self._assignees = []
        self._references = ReferencesManager()
        self._transcript = Transcript()
        self._transcript.addComment('Issue created')

    def manage_afterAdd(self, item, container):
        """ perform post-creation actions """
        BaseFolder.manage_afterAdd(self, item, container)

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
        

                                                
    ######################################################################
    # Followups
    ######################################################################

    def issue_followup(self, comment='', assignees=[], RESPONSE=None):
        """ issue followup handling """
        te = TranscriptEntry()
        te.addChange('assignees', self._assignees, assignees)
        self._assignees = assignees 
        if comment: te.addComment(comment)
        self._transcript.add(te)
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

        tracker = getattr(self, reference.tracker, None)
        if not tracker:
            raise ValueError('Tracker does not exist: %s' % reference.tracker)

        if getattr(tracker.aq_base, str(reference.ticketnumber), None) is None:
            raise ValueError('Ticket number does not exist: %s' % reference.ticketnumber)

        ref = Reference(reference.tracker, reference.ticketnumber, reference.comment)
        self._references.add(ref)
 
        te = TranscriptEntry()
        te.addReference(reference.tracker, reference.ticketnumber, reference.comment)
        self._transcript.add(te)

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
            
            te = TranscriptEntry()
            te.addUpload(file_id, comment)
            self._transcript.add(te)

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

        te = TranscriptEntry()
        for name in REQUEST.form.keys():
            new = REQUEST.get(name, None)
            old = getattr(self, name, None)
            if old:
                if str(old) != str(new): # Archetypes does not use Zope converters
                    te.addChange(name, old, new)
        self._transcript.add(te)

    def post_validate(self, REQUEST, errors):
        """ Hook to perform post-validation actions. We use this
            to reindex the issue.
        """
        self.reindexObject()

    def add_issue(self, RESPONSE):
        """ redirect to parent """
        return self.aq_parent.add_issue(RESPONSE=RESPONSE)

    ######################################################################
    # Catalog stuff
    ######################################################################

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'reindexObject')
    def reindexObject(self):
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

        l.append(self._transcript.asXML()) # ATT: this should go better
        return ' '.join(l)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'updateSchema')
    def updateSchema(self, schema):
        """ update the schema """
        self.schema = schema

    def __len__(self):
        return len(self._transcript)


registerType(PloneIssueNG)

