"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Issue.py,v 1.8 2003/09/09 12:21:07 ajung Exp $
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

class Issue(BaseFolder, WatchList):
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
        )

    security = ClassSecurityInfo()

    def __init__(self, id, title, schema, **kw):
        self.schema = schema
        BaseFolder.__init__(self, id, **kw)
        self.initializeArchetype()
        self.wl_init()
        self.id = id
        self.title = title 
        self._references = ReferencesManager()
        self._transcript = Transcript()
        self._transcript.addComment('Issue created')
                                                
    ######################################################################
    # Archetypes callbacks 
    ######################################################################

    def archetypes_mutator(self, v, **kw):
        """ the Archetypes mutator callback.
            ATT: we pass the Field instance as kw-arg 'field'
            This requires a hacked Archetypes.BaseObject.py (lines 366ff)
        """
        field = kw['field']  # ATT: maybe sniff into the stack frames
        self.Schema()[field.getName()].storage.set(field.getName(), self, v, **kw)

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

    def post_validate(self, REQUEST, errors):
        """ Hook to perform post-validation actions. We use this
            to reindex the issue.
        """
        self.reindexObject()

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'reindexObject')
    def reindexObject(self):
        catalogs = [getattr(self, 'pcng_catalog'), getToolByName(self, 'portal_catalog', None)]
        for c in catalogs: c.indexObject(self)

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'updateSchema')
    def updateSchema(self, schema):
        """ update the schema """
        self.schema = schema



registerType(Issue)

