##parameters=key

# retrieve the unique values from the catalog for the given key

def mycmp(x, y):
    try:
        return cmp(int(x), int(y))
    except:
        return cmp(x, y)

values = context.pcng_catalog.uniqueValuesFor(key)
values = [v for v in values if v]
values.sort(mycmp)
return values
