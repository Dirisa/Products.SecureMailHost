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
