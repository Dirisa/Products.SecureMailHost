## Script (Python) "formmailer_validator"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError

state = context.portal_form_controller.getState(script,
                                               is_validator = 1)

form  = context.form

try:  
   form.validate_all_to_request(context.REQUEST)
except FormValidationError, e:
   for err in e.errors:
       state.setError(err.field_id,err.error_text, new_status='failure')

return state
