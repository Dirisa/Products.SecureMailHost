##parameters=group_id

# return all user ids of a particular group

try:
    GT = context.portal_groups.getGroupById(group_id)
    lst = [m.getId() for m in GT.getGroupMembers()]
    lst.sort()
    return lst
except:
    return  []

