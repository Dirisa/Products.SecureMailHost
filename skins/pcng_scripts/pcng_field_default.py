##parameters=field

# workaround for changes in the AT API

try:
    return field.getDefault()
except:
    return field.getDefault(context)
