clientMD5 = context.REQUEST.get('clientMD5',None)
if not clientMD5:
   state.setError('clientMD5', 'Please enter a value', new_status='failure')

if state.getErrors():
   state.set(portal_status_message='Please correct the errors shown.')

return state

