"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: migrate.py,v 1.15 2003/11/10 08:49:16 ajung Exp $
"""


"""
Migration script for CMFCollectorNG to PloneCollectorNG

ATTENTION:

RUNNING THIS SCRIPT MIGHT DAMAGE YOUR PLONE SITE OR OVERRIDE SETTINGS OF YOUR
PLONE IF NOT APPLIED AND CONFIGURED PROPERLY. RUN THIS SCRIPT AT YOUR OWN RISK.
PERFORM A BACKUP OF YOUR DATA.FS **BEFORE** RUNNING THIS SCRIPT.  DO NOT
COMPLAIN IN CASE OF A FAILURE OR DATA LOSS. YOU HAVE BEEN WARNED!!!!!!!!!!!
"""


from Products.PloneCollectorNG.Collector import PloneCollectorNG
from Products.PloneCollectorNG.Issue import PloneIssueNG
from zLOG import LOG,INFO,ERROR,WARNING

ENFORCE_STATUS = 1  # set this to 1 to set the destination state based on the transcript information
ENFORCE_ASSIGNEES = 1 # set this to 1 to migrate the assignees based on transcript information

class record:

    def __init__(self):
        self._k = []

    def set(self, k, v):
        if not k in self._k:                   
            self._k.append(k)
        setattr(self, k, v)

    def keys(self):
        return self._k


def migrate_trackers(self, url_from='/trackers', url_to='/plone'):
    tracker_root = self.restrictedTraverse(url_from)
    plone_root = self.restrictedTraverse(url_to)

    # Remove the comment below to migrate the users as well
    # ATT: using migrate_acl_users() might *OVERRIDE* exisiting
    # user accounts on the destation site. BE WARNED !!!!!!

    #  migrate_acl_users(tracker_root, plone_root)

    # Remove the comment below to migrate the portal_memberdata.
    # ATT: using migrate_memberdata() might *OVERRIDE* exisiting
    # settings on the destation site. BE WARNED !!!!!!

    #  migrate_memberdata(tracker_root, plone_root)
   
    trackers = tracker_root.objectValues('CMF CollectorNG')
    for tracker in trackers:
        migrate_tracker(tracker, plone_root)

    return 'done'


def migrate_acl_users(source, dest):
    """ migrate all users """

    acl_users = source.acl_users
    dest_acl_users = dest.acl_users

    for u in acl_users.getUsers():
        dest_acl_users._addUser(u.getUserName(),
                                u._getPassword(),
                                u._getPassword(),
                                u.getRoles(),
                                u.getDomains())

def migrate_memberdata(source, dest):

    source_ms = source.portal_membership
    dest_ms = dest.portal_membership

    for id in source_ms.listMemberIds():
        member = source_ms.getMemberById(id)
            
        dest_member = dest_ms.getMemberById(id)

        if dest_member is None:
            LOG('pcngmigration', ERROR, 'memberdata for "%s" not migrated' % id)
            continue

        email = member.getProperty('email')
        if not email:
            LOG('pcngmigration', WARNING, 'no email for "%s" found...faking it' % id)
            email = 'dummy@nospam.com'

        
        D = {'pcng_company' : member.getProperty('submitter_company'),
             'fullname' : member.getProperty('submitter_name'),
             'email' : email,
             'pcng_position' : member.getProperty('submitter_position'),
             'pcng_city' : member.getProperty('submitter_city'),
             'pcng_address' : member.getProperty('submitter_address'),
             'pcng_fax' : member.getProperty('submitter_fax'),
             'pcng_phone' : member.getProperty('submitter_phone'),
             'pcng_send_attachments' : member.getProperty('submitter_send_attachments')
            }

        dest_member.setMemberProperties(D)


def migrate_tracker(tracker, dest):

    print '-'*75
    print 'Migrating collector:', tracker.getId()

    try: dest.manage_delObjects(tracker.getId())
    except: pass

    collector = PloneCollectorNG(tracker.getId())
    dest._setObject(tracker.getId(), collector)
    collector = dest[tracker.getId()]

    # Schema migration
    migrate_schema(tracker, collector)

    issues = tracker.objectValues('CMF CollectorNG Issue')
    for issue in issues:
        migrate_issue(issue, collector)

    # Staff
    collector.set_staff(reporters=tracker.reporters,
                        managers=tracker.managers,
                        supporters=tracker.supporters)

    # Number of issues
    collector._num_issues = len(issues) + 1
    
    # Reindex issues
    collector.reindex_issues()


mapping = {
    'title' : ('title', 'issuedata'),
    'description' : ('description', 'issuedata'),
    'solution' : ('solution', 'issuedata'),
    'classification' : ('classification', 'issuedata'),
    'topic' : ('topic', 'issuedata'),
    'version_info' : ('version_info', 'issuedata'),
    'importance' : ('importance', 'issuedata'),
    'operating_system' : ('operating_system', 'issuedata'),
    'custom1' : ('custom1', 'issuedata'),
    'custom2' : ('custom2', 'issuedata'),
    'custom3' : ('custom3', 'issuedata'),

    'hours_needed' : ('progress_hours_needed', 'progress'),
    'hours_required' : ('progress_hours_estimated', 'progress'),
    'progress' : ('progress_percent_done', 'progress'),
    'deadline' : ('progress_deadline', 'progress'),

    'submitter_email' : ('contact_email', 'contact'),
    'submitter_address' : ('contact_address', 'contact'),
    'submitter_name' : ('contact_name', 'contact'),
    'submitter_phone' : ('contact_phone', 'contact'),
    'submitter_fax' : ('contact_fax', 'contact'),
    'submitter_position' : ('contact_position', 'contact'),
    'submitter_company' : ('contact_company', 'contact'),
    'submitter_city' : ('contact_city', 'contact'),
}

def migrate_schema(tracker, collector):
    """ migrate old configuration to Archetypes schema """

    from Products.Archetypes.public import StringField, DateTimeField, FloatField
    from Products.Archetypes.public import StringWidget, TextAreaWidget, SelectionWidget, MultiSelectionWidget
    from Products.Archetypes.public import Schema, DisplayList

    schema = Schema()
    PM = tracker.issuePropertyManager

    for oldfield in mapping.keys():
        new_field, schemata = mapping[oldfield]

        try:
            prop = PM.getPropertyById(oldfield)
        except KeyError:
            print 'No property "%s" found' % oldfield
            continue

        new_id,schemata = mapping[prop.getId()]

        # Determine AT Field
        if prop.getType() == 'date': field = DateTimeField
        elif prop.getType() == 'float': field = FloatField
        elif prop.getType() in ('textarea', 'select', 'text', 'select-multiple'): field = StringField
        else:
            raise ValueError('Unsupported field type: %s' % prop.getType())

        # Determine AT widget
        if prop.getType() in ('date', 'float', 'text'): widget = StringWidget()
        elif prop.getType() in ('textarea',): widget = TextAreaWidget()
        elif prop.getType() == 'select': widget = SelectionWidget(format='select')
        elif prop.getType() == 'select-multiple': widget = MultiSelectionWidget(format='select')
        else:
            raise ValueError('Unsupported field type: %s' % prop.getType())

        # Fill widget attributes
        widget.visible = 1
        widget.i18n_domain = 'plonecollectorng'
        widget.label = prop.getDescription()
        widget.label_msgid = 'label_' + widget.label

        # Fill field attributes
        D = {}
        D['mutator'] = 'archetypes_mutator'
        D['accessor'] = 'archetypes_accessor'
        D['edit_accessor'] = 'archetypes_accessor'
        D['schemata'] = schemata
        D['default'] = prop.getDefaultValue()
        D['required'] = prop.getMandatory()
        D['widget'] = widget
        if widget.__class__.__name__ in ('SelectionWidget', 'MultiSelectionWidget'):
            D['vocabulary'] = DisplayList(prop.getValuesAsList())

        if prop.getId() == 'topic':
            l = []
            for topic,subtopics in tracker.getSubtopics():
                for st in subtopics:
                    s = topic + '/' + st
                    l.append((s,s))
            D['vocabulary'] = DisplayList(l)
            

        # Create and add field to schema
        field = field(new_id, **D)
        schema.addField(field)

    # Check if all properties were migrated properly
    for id in PM.getPropertyIds():
        if id  in ('assignees','security_related', 'status', 'subtopic', 'topic'): continue
        if not id in mapping.keys():
            raise ValueError('unknown field "%s"' % id)

    collector.schema_init(schema)


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

    # Owner
    new_owner = collector.acl_users.getUser(issue.getOwner().getUserName())
    new_issue.changeOwnership(new_owner)
    
    # Migrate uploads
    ids = issue.objectIds()
    new_issue.manage_pasteObjects(issue.manage_copyObjects(ids))

    # Transcript
    transcript = new_issue.getTranscript()

    status = ''
    tr_assignees = []

    entries = [e for e in issue.transcript] 
    entries.reverse()
    for entry in entries:

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
                if change.getField() == 'Status':
                    status = change.getNew()

            elif change.__class__.__name__ == 'IncrementalChangeEvent':
                transcript.addIncrementalChange(change.getField(), 
                                                change.getRemoved(), 
                                                change.getAdded(), 
                                                created=ts,
                                                user=entry.getUser())   

                if change.getField().lower().find('zugewiesen') > -1 or \
                   change.getField().lower().find('assigned') > -1:
                    for u in change.getRemoved():
                        if u in tr_assignees: tr_assignees.remove(u)
                    for u in change.getAdded():
                        if not u in tr_assignees: tr_assignees.append(u)


            else:
                raise TypeError(change)


        for upload in entry.getUploads():
                transcript.addUpload(upload.getFileId(),
                                     upload.getComment(),
                                     created=ts,
                                     user=entry.getUser())   

    # Workflow
    old_state = new_issue.status()

    if ENFORCE_STATUS == 1 and status:
        new_state = status  
    else:
        new_state = issue.status()

    if ENFORCE_ASSIGNEES:
        assignees = tr_assignees
    else:
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

        new_issue.workflow_history['pcng_issue_workflow'][-1]['assigned_to'] = assignees
    
