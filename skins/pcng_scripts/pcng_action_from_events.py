##parameters=events

# Return action info from a group of actions

for e in events:
    if e.getType() == 'action':
        return '(%s)' % e.getAction()

return ''
