
# perform a search

R = context.REQUEST
query = {}

def toQuery(key):
    if R.has_key(key):
        query[key]= R[key]


toQuery('SearchableText')
toQuery('status')
toQuery('Creator')
toQuery('assigned_to')


if len(query) == 0:
    query['status'] = ('Accepted', 'Pending')

print query
results = context.pcng_catalog.searchResults(query)
print results
return results
