## Python Script "clipboard_clear"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cb_id
##title=Clear all objects from given clipboard
##

from Products.PloneClipboard.utils import set_query_values

REQUEST = context.REQUEST
url = REQUEST.get('HTTP_REFERER')

tool = context.ploneclipboard_tool
refbag = tool.getClipboard(cb_id)
refbag.clear()
msg = 'Cleared %s.' % refbag.title_or_id()
new_url = set_query_values(url, portal_status_message=msg)

return REQUEST.RESPONSE.redirect(new_url)
