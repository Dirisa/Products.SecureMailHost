def fix(self):
    wftool = self.portal_workflow  # evil
    for issue in self.objectValues('PloneIssueNG'):
        print issue.getId(), issue.assigned_to(), issue.status(), issue.validActions()
        events = issue.getTranscript().getEvents()
        for ev in events:
            if ev.getType()=='incrementalchange' and ev.getValue('field')=='Assignees':
                people = ev.getValue('added')
                print people
                issue.issue_followup('assign', 'created by migration tool', assignees=people)
    return 'done'
