##parameters=name

# Convert a DisplayList instance into a dictionary

d = {}
try:
    vocab = context.atse_getSchema()[name].vocabulary
    for k, v in vocab.items():
        d[k] = v
except:
    pass

return d

