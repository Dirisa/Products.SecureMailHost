# Controller Python Script "formmailer_send"
##bind context=context
##bind state=state
##parameters=
##title=Sends a formmailer form.
##
if context.getCPYAction().strip():
    return state.set(next_action='traverse_to:'+context.getCPYAction())

context.send_form()

if context.getSentRedirect().strip():
    return state.set(next_action='redirect_to:'+context.getSentRedirect())

return state

