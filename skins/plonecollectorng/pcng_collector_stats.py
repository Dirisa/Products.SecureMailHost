# Retrieve some statistics about tickets

from AccessControl import getSecurityManager
username = getSecurityManager().getUser().getUserName()

catalog = context.pcng_catalog

# determine total number of tickets
total_tickets = len(context.objectIds(('PloneIssueNG',)))

# determine number of open tickets
query = {}
query['Type'] = 'Plone Issue NG'
query['status'] = ['pending', 'accepted']
open_tickets = len(catalog(REQUEST=query))

# determine number of my created tickets
query = {}
query['Type'] = 'Plone Issue NG'
query['status'] = ['pending', 'accepted']
query['Creator'] = username
my_created_tickets = len(catalog(REQUEST=query))

# determine number of tickets I am assigned to
query = {}
query['Type'] = 'Plone Issue NG'
query['status'] = ['pending', 'accepted']
query['assigned_to'] = username
my_assigned_tickets = len(catalog(REQUEST=query))

return (total_tickets, open_tickets, my_created_tickets, my_assigned_tickets)
