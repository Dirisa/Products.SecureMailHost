## Controlled Python Script "validate_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=title='', participation_mode='', view_mode=''
##title=Validates an object title
##

# validate view and particpation mode

if not participation_mode and not view_mode:
    return state # wrong film

if participation_mode == 'staff':
    if not view_mode in ('staff', 'restrictedstaff'):
        state.setError('view_mode', 'Invalid value for participation mode "staff"', 'input_required')
elif participation_mode == 'authenticated':
    if not view_mode in ('authenticated', 'staff', 'restrictedstaff'):
        state.setError('view_mode', 'Invalid value for participation mode "authenticated"', 'input_required')
        
if state.getErrors():
    return state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    return state

return state
