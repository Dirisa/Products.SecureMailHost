
# return a sequence of searchable fields

names = ['status', 'creator', 'assigned_to', 'importance', 'topic']

schema = context.atse_getSchema()
fields = []

for n in names:

    try: 
        field = schema[n]
        fields.append( (n, field) )
    except:
        fields.append( (n, None) )
        pass

return fields
