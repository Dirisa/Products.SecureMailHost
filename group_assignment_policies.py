"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: group_assignment_policies.py,v 1.3 2004/02/24 12:08:35 ajung Exp $
"""

""" 
Handle groups assignment

Issues can be assigned to a group where the group is either a GRUF group
or PloneCollectorNG topic group. Currently we implement only a simple
assignment policy where all members of a group are assigned to an issue.
"""

def usersForTopicGroup(context, group):
    return list(context.get_topics_user()[group])

def usersForGrufGroup(context, group):
    try:
        group = context.portal_groups.getGroupById(group)
        return [m.getUserName() for m in group.getGroupMembers()]
    except:
        return ()

def getUsersForGroups(context, groups):
    """ return a list of user IDs that belong to the given groups """

    try:
        gruf_groups = context.portal_groups.listGroupIds()
    except:
        gruf_groups = []

    topic_groups = context.get_topics_user()

    lst = []
    for group in groups:
        if group in topic_groups.keys():
            lst.extend(usersForTopicGroup(context, group))        
        if group in gruf_groups:
            lst.extend(usersForGrufGroup(context, group))        
    return lst        
