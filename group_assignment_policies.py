"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: group_assignment_policies.py,v 1.1 2004/02/23 16:59:36 ajung Exp $
"""

""" 
Handle groups assignements
"""

def usersForTopicGroup(context, group):
    return list(context.get_topics_user()[group])

def usersForGrufGroup(context, group):
    try:
        group = context.portal_groups.getGroupById(group)
        ## FIX THIS !!!!
        return group.getUserNames()
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
