# determine the user's role in the context of a PloneCollectorNG 
# issue instance

from AccessControl import getSecurityManager


if context.meta_type == 'PloneCollectorNG':
    collector = context
elif context.meta_type == 'PloneIssueNG':
    collector = context.aq_parent
else:
    raise ValueError('unknown context')

user = getSecurityManager().getUser()
roles = user.getRolesInContext(collector)

for role in ('TrackerAdmin', 'Supporter', 'Reporter', 'Authenticated', 'Anonymous'):
    if role in roles:
        return role

raise ValueError('no matching role for user "%s" found' % user.getUserName())
