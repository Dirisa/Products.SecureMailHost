# Show a list of all users and their roles in all trackers
# (Visible only for Managers)

mbrtool = context.portal_membership
users = context.acl_users.getUserNames()
users.sort()

collectors = [ c.getObject() for c in context.portal_catalog(meta_type="PloneCollectorNG") ]

for user in users:
 
    u = context.acl_users.getUser(user)

    member = mbrtool.getMemberById(u.getUserName())

    print '%s (%s)' % (user, member.getProperty('email'))

    for c in collectors:
        roles = u.getRolesInContext(c)
        roles = [r for r in roles  if r not in ('Authenticated', 'Member') ]
        if roles:
            print "\t", c.getId(), roles

    print 

return printed
