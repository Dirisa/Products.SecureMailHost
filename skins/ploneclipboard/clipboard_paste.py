## Python Script "clipboard_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=cb_id
##title=Paste objects into a clipboard
##

from Products.PloneClipboard.utils import set_query_values

REQUEST = context.REQUEST
url = REQUEST.get('HTTP_REFERER')

tool = context.ploneclipboard_tool
refbag = tool.getClipboard(cb_id)
before = len(refbag.objectIds())
refbag.manage_pasteObjects(REQUEST=REQUEST)
added = len(refbag.objectIds()) - before
msg = '%s item(s) added to %s.' % (added, refbag.title_or_id())
new_url = set_query_values(url, portal_status_message=msg)

return REQUEST.RESPONSE.redirect(new_url)
