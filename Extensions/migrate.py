"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: migrate.py,v 1.3 2003/11/04 19:35:27 ajung Exp $
"""

"""Migration script for CMFCollectorNG to PloneCollectorNG"""

from Products.PloneCollectorNG.Collector import PloneCollectorNG
from Products.PloneCollectorNG.Issue import PloneIssueNG

DEST_ID = 'trackers'

class record:

    def __init__(self):
        self._k = []

    def set(self, k, v):
        if not k in self._k:
            self._k.append(k)
        setattr(self, k, v)

    def keys(self):
        return self._k


def migrate_trackers(self, url_from='/trackers', url_to='/plone1')):
    tracker_root = self.restrictedTraverse(url_from)
    plone_root = self.restrictedTraverse(url_to)

    trackers = tracker_root.objectValues('CMF CollectorNG')
    for tracker in trackers:
        migrate_tracker(tracker, dest)

    return 'done'

def migrate_tracker(tracker, dest):

#    if tracker.getId() != 'HaufeReader': return
    print '-'*75
    print 'Migrating collector:', tracker.getId()

    try: dest.manage_delObjects(tracker.getId())
    except: pass

    collector = PloneCollectorNG(tracker.getId())
    dest._setObject(tracker.getId(), collector)
    collector = dest[tracker.getId()]

    issues = tracker.objectValues('CMF CollectorNG Issue')
    for issue in issues:
        migrate_issue(issue, collector)

    collector._num_issues = len(issues)

def migrate_issue(issue, collector):
    print 'Migrating issue:', issue

    new_issue = PloneIssueNG(issue.getId(), issue.title, collector.schema_getWholeSchema())
    collector._setObject(issue.getId(), new_issue)
    new_issue = getattr(collector, issue.getId())

    P = record()
    P.set('title', issue.title)
    P.set('description',  issue.description)
    P.set('solution', issue.solution)
    P.set('topic',  issue.topic + "/" + issue.subtopic)
    P.set('classification',  issue.classification)
    P.set('importance',  issue.importance)

    for f in ('submitter_name', 'submitter_email' , 'submitter_company',
              'submitter_position' , 'submitter_city', 'submitter_phone',
              'submitter_fax'):
        P.set(f.replace('submitter', 'contact'), getattr(issue, f, ''))

    P.set('progress_hours_estimated', issue.hours_required)
    P.set('progress_hours_needed', issue.hours_needed)
    P.set('progress_deadline', issue.deadline)
    P.set('progress_percent_done', issue.progress)

    new_issue.setParameters(P)
    
    # Migrate uploads
    ids = issue.objectIds()
    new_issue.manage_pasteObjects(issue.manage_copyObjects(ids))

    # Transcript
    transcript = new_issue.getTranscript()
    for entry in issue.transcript:

        ts = entry.getTimestamp().timeTime()

        for comment in entry.getComments():
            transcript.addComment(comment.getComment(), 
                                  user=entry.getUser(), 
                                  created=ts)

        for change in entry.getChanges():
            if change.__class__.__name__ == 'ChangeEvent':
                transcript.addChange(change.getField(), 
                                     change.getOld(), 
                                     change.getNew(), 
                                     created=ts,
                                     user=entry.getUser())   
            elif change.__class__.__name__ == 'IncrementalChangeEvent':
                transcript.addIncrementalChange(change.getField(), 
                                                change.getRemoved(), 
                                                change.getAdded(), 
                                                created=ts,
                                                user=entry.getUser())   
            else:
                raise TypeError(change)


        for upload in entry.getUploads():
                transcript.addUpload(upload.getFileId(),
                                     upload.getComment(),
                                     created=ts,
                                     user=entry.getUser())   


    # Workflow
    new_state = issue.status()
    old_state = new_issue.status()
    assignees = issue.assigned_to()
    
    if new_state.lower() != old_state.lower():

        wftool = collector.portal_workflow  # evil
        
        if new_state == 'Resolved':
            wftool.doActionFor(new_issue, 'accept', assignees=assignees)
            wftool.doActionFor(new_issue, 'resolve', assignees=assignees)
        elif new_state == 'Rejected':
            wftool.doActionFor(new_issue, 'accept', assignees=assignees)
            wftool.doActionFor(new_issue, 'reject', assignees=assignees)
        elif new_state == 'Deferred':
            wftool.doActionFor(new_issue, 'accept', assignees=assignees)
            wftool.doActionFor(new_issue, 'defer', assignees=assignees)
        elif new_state in ('Accepted',):
            wftool.doActionFor(new_issue, 'accept', assignees=assignees)
        else: 
            raise ValueError(new_state)
    
