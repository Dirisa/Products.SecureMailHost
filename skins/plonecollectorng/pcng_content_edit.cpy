## Script (Python) "pcng_content_edit"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=''

REQUEST = context.REQUEST

new_context = None
if context.meta_type == 'PloneIssueNG':
    if context.portal_factory.isTemporary(context):
        id = context.new_issue_number()
        new_context = context.portal_factory.doCreate(context, id)
        new_context.processForm()
    else:
        try:        
            id = int(context.getId())
            context.processForm()
            new_context = context
        except:
            id = context.new_issue_number()
            parent = context.aq_parent
            context.processForm()
            parent.manage_renameObjects([context.getId()], [id])
            new_context = getattr(parent, id)            
            new_context.processForm()

        
else:
    new_context = context.portal_factory.doCreate(context, id)
    new_context.processForm()

portal_status_message = REQUEST.get('portal_status_message', new_context.translate('changes_saved', 'Content changes saved'))
return state.set(status='success',\
                 context=new_context,\
                 portal_status_message=portal_status_message)

