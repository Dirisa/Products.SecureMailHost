##parameters=query_id=''

# Modify the saved searches member properties

if query_id=='':
    msg = context.translate(msgid='no_search_for_deletion', default='No search for deletion selected', domain='plonecollectorng')
    context.REQUEST.RESPONSE.redirect('pcng_member_preferences?portal_status_message=%s' % msg)
    return

mstool = context.portal_membership

if mstool.isAnonymousUser(): 
    msg = context.Translate('unknown_user', 'Unknown user')
    context.REQUEST.RESPONSE.redirect('pcng_view?portal_status_message=%s' % msg)
    return

member = mstool.getAuthenticatedMember()
saved_searches = member.getProperty('pcng_saved_searches', [])

# delete a search 
if context.REQUEST.has_key('delete'):
    saved_searches = [s for s in saved_searches if not s.startswith(query_id)]

member.setProperties({'pcng_saved_searches' : saved_searches})

msg = context.Translate('changes_saved', 'Changes saved')
context.REQUEST.RESPONSE.redirect('pcng_member_preferences?portal_status_message=%s' % msg)

