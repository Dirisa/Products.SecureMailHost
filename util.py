def getUserName():
    """ return user name """
    from AccessControl import getSecurityManager
    return getSecurityManager().getUser().getUserName()


def add_local_role(obj, userid, role):
    """Add object role for userid if not already there."""
    roles = list(obj.get_local_roles_for_userid(userid))
    if role not in roles:
        roles.append(role)
        obj.manage_setLocalRoles(userid, roles)


def remove_local_role(obj, userid, role):
    """Add object role for userid if not already there."""
    roles = list(obj.get_local_roles_for_userid(userid))
    roles.remove(role)
    if roles:
        obj.manage_setLocalRoles(userid, roles)
    else:
        obj.manage_delLocalRoles([userid])


def users_for_local_role(obj, userids, role):
    """Give only designated userids specified local role.

    Return 1 iff any role changes happened."""
    already = []
    changed = 0
    for u in obj.users_with_local_role(role):
        if u in userids:
            already.append(u)
        else:
            changed = 1
            remove_local_role(obj, u, role)
    for u in userids:
        if u not in already:
            changed = 1
            add_local_role(obj, u, role)
    return changed
