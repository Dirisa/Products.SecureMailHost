
# return a sequence of searchable fields

names = ['status', 'Creator', 'assigned_to', 'importance', 'topic']
names.extend([f.getName() for f in context.atse_getSchema().fields() if getattr(f, 'createindex', 0) == 1])                                
return names
