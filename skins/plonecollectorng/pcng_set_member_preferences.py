# store member preferences for PloneCollectorNG

from AccessControl import getSecurityManager

mstool = context.portal_membership

if mstool.isAnonymousUser(): 
    context.REQUEST.RESPONSE.redirect('pcng_member_preferences?portal_status_message=Unknown%20user')
    return

member = mstool.getAuthenticatedMember()
member.setProperties(context.REQUEST)

context.REQUEST.RESPONSE.redirect('pcng_member_preferences?portal_status_message=Preferences%20updated')

