##parameters=status

# reformat the workflow state to a more readable string

if status.find('_') == -1: # not found:
    return status.capitalize()
f = status.split('_', 1)
return '%s (%s)' % (f[0].capitalize(), f[1])

