# return list of all groups or an empty list

try:
    return context.portal_groups.listGroupIds()
except:
    return []
