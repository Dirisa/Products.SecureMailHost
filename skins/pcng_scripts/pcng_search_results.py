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
for idx_id, idx_type in context.pcng_catalog.getIndexes():
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
        date = context.pcng_tool.String2DateTime(d_value)

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

# Filter results by role and view mode
view_mode = context.getView_mode()
user_role = context.pcng_user_role()

no_auth = False
if view_mode == 'restricted' and not user_role in ('Manager', 'TrackerAdmin', 'Supporter'):
    no_auth = True
elif view_mode == 'staff' and not user_role in ('Manager', 'TrackerAdmin', 'Supporter', 'Reporter'):
    no_auth = True
elif view_mode == 'authenticated' and not user_role in ('Manager',  'TrackerAdmin', 'Supporter', 'Reporter', 'Authenticated'):
    no_auth = True

if no_auth:
    return context.REQUEST.RESPONSE.redirect('pcng_no_permission')

if sort_on: results.sort(query_sort)
if debug: return printed

# Save result in session
try:
    def mysort(x,y):
        try:
            return cmp(int(x[1]), int(y[1]))
        except:
            return cmp(str(x[1]), str(y[1]))


    lst = [ (b.getURL(), b.getId, b.Title) for b in results]
    lst.sort(mysort)
    R.SESSION['pcng_searchresults'] = lst
except:
    pass
return results
