# Show a list of all users and their roles in all trackers
# (Visible only for Managers)

mbrtool = context.portal_membership
users = context.acl_users.getUserNames()
users.sort()

context.REQUEST.RESPONSE.setHeader('content-type', 'text/plain; charset=utf-8')

ManageCollector = 'PloneCollectorNG: Manage PloneCollectorNG'
EditCollectorIssue = 'PloneCollectorNG: Edit PloneCollectorNG issue'
AddCollectorIssue = 'PloneCollectorNG: Add PloneCollectorNG issue'
AddCollectorIssueFollowup = 'PloneCollectorNG: Add PloneCollectorNG issue followup'
EmailSubmission = 'PloneCollectorNG: Submit issue through email'

permissions = [ManageCollector, EditCollectorIssue, AddCollectorIssue, 
               AddCollectorIssueFollowup ,EmailSubmission ]

for user in users:
 
    u = context.acl_users.getUser(user)
    member = mbrtool.getMemberById(u.getUserName())
    print user

    for p in permissions:
        allowed = member.has_permission(p, context)
        if allowed:
            print '\t' + p
    print 

return printed

