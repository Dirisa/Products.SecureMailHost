## Script (Python) "content_edit"
##title=Edit content
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None

obj = context.portal_factory.doCreate(context, id)
obj.processForm()

REQUEST = context.REQUEST
portal_status_message = REQUEST.get('portal_status_message', 'Content changes saved.')

# handle navigation for multi-page edit forms
next = REQUEST.get('form_next',None) != None
previous = REQUEST.get('form_previous',None) != None
if next or previous:
    fieldset = REQUEST.get('fieldset', None)

    schematas = obj.Schemata().keys()
    if next:
        schematas.reverse()

    next_schemata = None
    for fs in schematas:
        if fs != 'metadata':
            if fieldset == fs:
                if next_schemata == None:
                    raise 'Unable to find next field set after %s' % fieldset
                return ('next_schemata', obj, {'fieldset':next_schemata, 'portal_status_message':portal_status_message})
            next_schemata = fs

return ('success', obj, {'portal_status_message':portal_status_message})
