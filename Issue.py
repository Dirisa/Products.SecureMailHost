"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: Issue.py,v 1.3 2003/09/07 07:12:27 ajung Exp $
"""

from AccessControl import getSecurityManager, ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.public import BaseFolder, registerType

from Transcript import Transcript, TranscriptEntry
from config import ManageCollector, AddCollectorIssue, AddCollectorIssueFollowup
from config import IssueWorkflowName
from References import Reference, ReferencesManager
import util

class Issue(BaseFolder):
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
        self.id = id
        self.title = title 
        self._references = ReferencesManager()
        BaseFolder.__init__(self, id, **kw)
        self.transcript = Transcript()
        self.transcript.addComment('Issue created')

    ######################################################################
    # References handling
    ######################################################################

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
        self.transcript.add(te)

        if RESPONSE is not None:
           RESPONSE.redirect('pcng_issue_references?portal_status_message=Reference%20has%20been%20stored')

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
            self.transcript.add(te)

            if RESPONSE is not None:
                RESPONSE.redirect('pcng_issue_references?portal_status_message=File%20has%20been%20uplopaded')
        else:
            if RESPONSE is not None:
                RESPONSE.redirect('pcng_issue_references?portal_status_message=Nothing%20to%20be%20uploaded')


registerType(Issue)

