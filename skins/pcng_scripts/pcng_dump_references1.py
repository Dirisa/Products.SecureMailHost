# Dump references

if context.meta_type == 'PloneCollectorNG':
    collectors = [context]
else:
    collectors = context.objectValues('PloneCollectorNG')


for c in collectors:
  for o in c.objectValues('PloneIssueNG'):

     try:
        refs = o.getForwardReferences()
     except Exception,e:
        print 'Fehler bei:', c.getId(), o.getId(), e
        continue

     if refs:
        for r in refs:
            to = r.getTargetObject()
            if to:
                print o.absolute_url(1), to.absolute_url(1), r.comment
            else:
                print o.absolute_url(1), 'Fehler', r.comment
      
return printed

