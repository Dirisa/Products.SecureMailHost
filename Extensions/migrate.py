""" Migration script for CMFCollectorNG to PloneCollectorNG """

from OFS.Folder import manage_addFolder
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

def migrate_trackers(self):
    self = self.restrictedTraverse('/plone')
    root = self.restrictedTraverse('/trackers')

    try: self.manage_delObjects(DEST_ID)
    except: pass

    manage_addFolder(self, DEST_ID, DEST_ID)
    dest = self[DEST_ID]

    trackers = root.objectValues('CMF CollectorNG')

    for tracker in trackers:
        migrate_tracker(tracker, dest)

    return 'done'

def migrate_tracker(tracker, dest):

    if tracker.getId() != 'HaufeReader': return
    print '-'*75
    print 'Migrating collector:', tracker.getId()

    collector = PloneCollectorNG(tracker.getId())
    dest._setObject(tracker.getId(), collector)

    collector = dest[tracker.getId()]
    issues = tracker.objectValues('CMF CollectorNG Issue')

    for issue in issues:
        migrate_issue(issue, collector)

def migrate_issue(issue, collector):
#    if issue.getId() != '16': return    
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
    for entry in issue.transcript:

        ts = entry.getTimestamp().timeTime()

        for comment in entry.getComments():
            new_issue.getTranscript().addComment(comment.getComment(), 
                                                 user=entry.getUser(), 
                                                 created=ts)

        for change in entry.getChanges():
            if change.__class__.__name__ == 'ChangeEvent':
                new_issue.getTranscript().addChange(change.getField(), 
                                                    change.getOld(), 
                                                    change.getNew(), 
                                                    created=ts,
                                                    user=entry.getUser())   
            elif change.__class__.__name__ == 'IncrementalChangeEvent':
                new_issue.getTranscript().addIncrementalChange(change.getField(), 
                                                               change.getAdded(), 
                                                               change.getRemoved(), 
                                                               created=ts,
                                                               user=entry.getUser())   
            else:
                raise TypeError(change)


        for upload in entry.getUploads():
                new_issue.getTranscript().addUpload(upload.getFileId(),
                                                    upload.getComment(),
                                                    created=ts,
                                                    user=entry.getUser())   

