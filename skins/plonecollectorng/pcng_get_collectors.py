
# Return a list of dictionaries with informations on all
# PloneCollectorNG instance in the local folder

from AccessControl import getSecurityManager
user = getSecurityManager().getUser()

l = []
for c in context.objectValues('PloneCollectorNG'):
    d = {'id' : c.getId(), 
         'url' : c.absolute_url(), 
         'title' : c.title,
         'view_permission' : user.has_permission('View', c),
         }

    try:
        d['stats'] = c.pcng_collector_stats()
    except:
        d['state'] = None

    l.append(d)

l.sort(lambda x,y: cmp(x['id'], y['id']))
return l
