## Script (Python) "addAssignees"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=assigned_to, assignees
##title=
##
for person in assignees:

  if not person in assigned_to:
    assigned_to.append(person)

return assigned_to
