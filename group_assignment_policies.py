"""
PloneCollectorNG - A Plone-based bugtracking system

(C) 2002-2004, Andreas Jung

ZOPYX Software Development and Consulting Andreas Jung
Charlottenstr. 37/1
D-72070 Tübingen, Germany
Web: www.zopyx.com
Email: info@zopyx.com 

License: see LICENSE.txt

$Id: group_assignment_policies.py,v 1.7 2004/11/12 15:37:52 ajung Exp $
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
