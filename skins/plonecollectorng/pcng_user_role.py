# determine the user's role in the context of a PloneCollectorNG 
# issue instance

from AccessControl import getSecurityManager

user = getSecurityManager().getUser()
roles = user.getRolesInContext(context)

for role in ('TrackerAdmin', 'Supporter', 'Reporter', 'Authenticated', 'Anonymous'):
    if role in roles:
        return role

raise ValueError('no matching role for user "%s" found' % user.getUserName())
