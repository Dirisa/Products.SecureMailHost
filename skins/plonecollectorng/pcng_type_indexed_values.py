##parameters=index_id

# Determine the type of the indexed values for the index
# given by its 'index_id'

values = context.pcng_uniquevalsFor(index_id)
if len(values) == 0: return 'string'

if same_type(values[0], 0): return 'int'
elif same_type(values[0], 0.0): return 'float'
elif same_type(values[0], ''): return 'string'
elif same_type(values[0], u''): return 'ustring'
else: return 'string'
