##parameters=name

# Return the type of an index given by its name

try:
    index = context.pcng_catalog.Indexes[name]
    return index.meta_type
except:
    return None
