"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: util.py,v 1.7 2003/09/09 12:09:02 ajung Exp $
"""

import urllib

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


def isValidEmailAddress(email):
    """ validate an email address """

    at = email.find('@')
    pt = email.find('.')
    # Minimal lenght must be 8
    if len(email) <= 7 :
        return 0
    # We must have an @ but not first and not last
    if at == -1 or at == 0 or email[-1] == '@':
        return 0
    # Same applies for the point
    if pt == -1 or pt == 0 or email[-1] == '.':
        return 0
    # Only one @ is valid
    if email.find('@',at+1) > -1:
        return 0
    # @ and . cannot be together
    if email[at-1] == '.' or email[at+1] == '.':
        return 0
    # subdomain must have at least 2 letters
    if email[at+2] == '.':
        return 0
    # no spaces allowed
    if email.find(' ') > -1:
        return 0
    return 1


def remove_dupes(lst):
    """ remove dupes from a list """

    ret = []
    for l in lst:
        if not l in ret:
            ret.append(l)
    return ret 


def redirect(RESPONSE, dest, msg=None,**kw):
    from urllib import quote
    
    if RESPONSE is not None:    
        url = dest + "?"
        if msg:
            url += "portal_status_message=%s&" % quote(msg)
        if kw:
            url += '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in kw.items()])

        RESPONSE.redirect(url) 
