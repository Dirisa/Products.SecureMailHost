##parameters=username
# return list of all groups or a given user

try:
    return [g.getId() for g in context.portal_groups.getGroupsByUserId(username)]
except:
    return []
