## Script (Python) "send_notifications"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=state_change
##title=
##
issue = state_change.object
issue.send_notifications()
return 1
