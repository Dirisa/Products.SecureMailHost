"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: fix_workflow_histories.py,v 1.2 2004/06/29 13:08:33 ajung Exp $
"""

def fix_workflow_histories(self, old_wf='pcng_issue_workflow (PloneCollectorNG default workflow)'):
    """ Migrate the workflow history of all issues from the default workflow
        to the new workflow (by copying over the history in issue.workflow_history.
    """

    new_wf = self.collector_workflow        
    for issue in self.objectValues('PloneIssueNG'):
        H = issue.workflow_history
        if H.has_key(old_wf) and not H.has_key(new_wf):
            # create a copy, don't drop old history
            H[new_wf] = H[old_wf]
            issue.workflow_history = H
    return 'done'