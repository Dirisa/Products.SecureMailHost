# Controller Python Script "formmailer_send"
##bind context=context
##bind state=state
##parameters=
##title=Sends a formmailer form.
##
if context.getCpyaction().strip():
    return state.set(next_action='traverse_to:'+context.getCpyaction())

context.send_form()

if context.getSent_redirect().strip():
    return state.set(next_action='redirect_to:'+context.getSent_redirect())

return state.set(next_action='redirect_to:string:formmailer_sent')

