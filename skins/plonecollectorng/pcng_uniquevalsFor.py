##parameters=key

# retrieve the unique values from the catalog for the given key

values = context.pcng_catalog.uniqueValuesFor(key)
values = [v for v in values if v]
values.sort()
return values
