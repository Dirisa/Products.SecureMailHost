## Script (Python) "pcng_content_edit"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=''

REQUEST = context.REQUEST

context.processForm()

portal_status_message = REQUEST.get('portal_status_message', context.translate('changes_saved', 'Content changes saved'))
return state.set(status='success',\
                 context=context,\
                 portal_status_message=portal_status_message)

