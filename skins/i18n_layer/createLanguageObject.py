## Script (Python) "createLanguageObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id=None,type_name=None
##title=
##
from DateTime import DateTime
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST

if type_name is None:
    raise Exception

if id is None:
    raise Exception

context.invokeFactory(id=id, type_name=type_name)
o=getattr(context, id, None)

if o is None:
    raise Exception

# make created object an i18nlayer object
context.setI18NLayerAttributes(id)

view=''
try:
    view=o.getTypeInfo().getActionById('edit')
except:
    view=o.getTypeInfo().getActionById('view')
transaction_note(o.getTypeInfo().getId() + ' was created.')
return REQUEST.RESPONSE.redirect(o.absolute_url()+'/'+view)
