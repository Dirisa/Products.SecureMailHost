##parameters=debug=0
# perform a search

R = context.REQUEST
sort_on = R.get('sort_on', 'getId')
sort_direction = R.get('sort_direction', 'desc')
query = {}

def toQuery(key):
    if R.has_key(key):
        if key == 'SearchableText':
            if R[key]:
                query[key]= R[key] 
        else:
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
for idx_id, idx_type in context.getIndexes():
    toQuery(idx_id)

# Datefields 
d_value = R.get('datefield_value', None)
d_field = R.get('datefield', None)
d_direction = R.get('datefield_direction', None)

if d_value:
    try:
        dummy = int(d_value)
        date = DateTime() - dummy
    except:
        date = context.String2DateTime(d_value)

    if d_direction == 'since': qrange = 'min'
    elif d_direction == 'until': qrange = 'max'
    else:
        raise ValueError('invalid value for datefield_direction: %s' % d_direction)
    query[d_field] = {'query' : date, 'range' : qrange}    

# Default query
if len(query) == 0:
    query['status'] = ('accepted', 'pending')

if debug: print query
results = list(context.pcng_catalog.searchResults(query))

if sort_on: results.sort(query_sort)
if debug: return printed

# Save result in session
try:
    lst = [ (b.getURL(), b.getId, b.Title) for b in results]
    R.SESSION['pcng_searchresults'] = lst
except:
    pass

return results
