##parameters=key

# retrieve the unique values from the catalog for the given key

def mycmp(x, y):
    try:
        return cmp(int(x), int(y))
    except:
        return cmp(x, y)

values = []
for v in context.pcng_catalog.uniqueValuesFor(key):
    if same_type(v, []) or same_type(v, ()):
        values.extend(v)
    else:
        values.append(v)
values = [v for v in values if v]
values.sort(mycmp)
return values
