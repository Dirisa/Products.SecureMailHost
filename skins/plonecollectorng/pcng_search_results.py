##parameters=debug=0
# perform a search

R = context.REQUEST
sort_on = R.get('sort_on', 'getId')
sort_direction = R.get('sort_direction', 'desc')
query = {}

print sort_on
print sort_direction

def toQuery(key):
    if R.has_key(key):
        query[key]= R[key]


def query_sort(a, b):
    """ helper method to sort the result list """

    va = getattr(a, sort_on); vb = getattr(b, sort_on)

    # try to convert the values to ints
    try:
        va = int(va); vb = int(vb)
    except: pass
    if sort_direction == 'desc': return -1 * cmp(va, vb)
    else: return cmp(va, vb)  

# here starts the show

toQuery('SearchableText')
toQuery('status')
toQuery('Creator')
toQuery('assigned_to')

# Default query
if len(query) == 0:
    query['status'] = ('Accepted', 'Pending')

if debug:
    print query

results = list(context.pcng_catalog.searchResults(query))

if sort_on:
    results.sort(query_sort)

if debug:
    return printed
return results
