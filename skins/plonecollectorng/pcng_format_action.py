##parameters=action

# Reformat a workflow action to be displayed

action = action.capitalize()
action = action.replace('_', ' ')

if action == 'Restrict accepted': return 'Restrict'
return action 
