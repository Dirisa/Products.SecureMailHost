"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: group_assignment_policies.py,v 1.6 2004/10/10 14:26:09 ajung Exp $
"""

""" 
Handle groups assignment

Issues can be assigned to a group where the group is either a GRUF group
or PloneCollectorNG topic group. Currently we implement only a simple
assignment policy where all members of a group are assigned to an issue.
"""


from Products.CMFCore.utils import getToolByName
from config import CollectorTool

def usersForTopicGroup(context, topic):
    return context.getTopics().getUsersForTopic(topic)

def usersForGrufGroup(context, group):

    tool = getToolByName(context, CollectorTool)

    tracker_staff = [u['username'] for u in tool.getTrackerUsers(staff_only=1)]
    try:
        group = context.portal_groups.getGroupById(group)
        return [m.getUserName() for m in group.getGroupMembers() if m.getUserName() in tracker_staff]
    except:
        return ()

def getUsersForGroups(context, groups):
    """ return a list of user IDs that belong to the given groups """

    try:
        gruf_groups = context.portal_groups.listGroupIds()
    except:
        gruf_groups = []

    topics =  context.getTopics().getTopics()

    lst = []
    for group in groups:
        if  group in topics:
            lst.extend(usersForTopicGroup(context, group))        
        if group in gruf_groups:
            lst.extend(usersForGrufGroup(context, group))        
    return lst        
