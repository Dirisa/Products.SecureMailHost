"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

License: see LICENSE.txt

$Id: util.py,v 1.19 2004/04/14 19:20:10 ajung Exp $
"""

import urllib

def getUserName():
    """ return user name """
    from AccessControl import getSecurityManager
    return getSecurityManager().getUser().getUserName()


def addLocalRole(obj, userid, role):
    """ add a local role for a user """
    roles = list(obj.get_local_roles_for_userid(userid))
    if role not in roles:
        roles.append(role)
        obj.manage_setLocalRoles(userid, roles)


def removeLocalRole(obj, userid, role):
    """ remove a local role from obj """
    roles = list(obj.get_local_roles_for_userid(userid))
    roles.remove(role)
    if roles:
        obj.manage_setLocalRoles(userid, roles)
    else:
        obj.manage_delLocalRoles([userid])


def adjustLocalRoles(obj, userids, role):
    """ adjust local roles for a role and a list of users """

    already = []
    changed = 0
    for u in obj.users_with_local_role(role):
        if u in userids:
            already.append(u)
        else:
            changed = 1
            removeLocalRole(obj, u, role)
    for u in userids:
        if u not in already:
            changed = 1
            addLocalRole(obj, u, role)
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


def lists_eq(l1, l2):
    """ compare two lists """   
    l1 = list(l1); l2 = list(l2)
    l1.sort(); l2.sort()
    return l1==l2


def redirect(RESPONSE, dest, msg=None,**kw):
    
    if RESPONSE is not None:    
        url = dest + "?"
        if msg:
            url += "portal_status_message=%s&" % urllib.quote(msg)
        if kw:
            url += '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in kw.items()])
        RESPONSE.redirect(url) 


def safeGetProperty(userobj, property, default=None):
    """Defaulting user.getProperty(), allowing for variant user folders."""
    try:
        if not hasattr(userobj, 'getProperty'):
            return getattr(userobj, property, default)
        else:
            return userobj.getProperty(property, default)
    except:
        # We can't just itemize the possible candidate exceptions because one
        # is a string with spaces, which isn't interned and hence object id
        # won't match.  Sigh.
        import sys
        exc = sys.exc_info()[0]
        if (exc == 'Property not found'
            or isinstance(exc, TypeError)
            or isinstance(exc, AttributeError)
            or isinstance(exc, LookupError)):
            try:
                # Some (eg, our old LDAP user folder) support getProperty but
                # not defaulting:
                return userobj.getProperty(property)
            except:
                return default
        else:
            raise

def encrypt(text, key):
    """ AES Encryption """
    try:
        from Crypto.Cipher import AES
    except ImportError:
        from zLOG import LOG, ERROR
        LOG('plonecollectorng', ERROR, 'PyCrypto (www.amk.ca/python/code/crypto) is required')
        raise

    obj = AES.new(key, AES.MODE_ECB)

    if len(text) % 16 != 0: # padding
        text += ' ' *(16-(len(text)%16)) 
    return obj.encrypt(text)


def decrypt(text, key):
    """ AES Decryption """
    try:
        from Crypto.Cipher import AES
    except ImportError:
        from zLOG import LOG, ERROR
        LOG('plonecollectorng', ERROR, 'PyCrypto (www.amk.ca/python/code/crypto) is required')
        raise
    
    obj = AES.new(key, AES.MODE_ECB)
    return obj.decrypt(text)
    
