## Python Script "search_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=paths
##title=Copy object from any form that provides paths
##

from Products.PloneClipboard.utils \
     import set_query_values, copy_objects_by_path

REQUEST = context.REQUEST
url = REQUEST.get('HTTP_REFERER')

copy_objects_by_path(context, paths)

msg = 'Item(s) copied.'
new_url = set_query_values(url, portal_status_message=msg)

return REQUEST.RESPONSE.redirect(new_url)
