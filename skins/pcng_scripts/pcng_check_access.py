
if context.isCollectorContext():
    return True

elif context.isIssueContext():

    # Filter results by role and view mode
    view_mode = context.getView_mode()
    user_role = context.pcng_user_role()

    if view_mode == 'restricted' and user_role in ('Manager', 'TrackerAdmin', 'Supporter'):
        return True
    elif view_mode == 'staff' and user_role in ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter'):
        return True
    elif view_mode == 'authenticated' and user_role in ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter', 'Authenticated'):
        return True

msg = 'Permission denied'
return context.REQUEST.RESPONSE.redirect('pcng_no_permission?portal_status_message=%s' % msg)

