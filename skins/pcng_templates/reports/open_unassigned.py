# all open and unassigned issues

rows =  context.pcng_catalog(status={'query' : ('pending', 'accepted')}, sort_on='created')
rows = [r for r in rows if len(r.assigned_to)==0]
return 'Open unassigned tickets', rows     
