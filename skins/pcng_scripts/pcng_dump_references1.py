# Dump references

for c in context.objectValues('PloneCollectorNG'):
  for o in c.objectValues('PloneIssueNG'):

     try:
        refs = o.getForwardReferences()
     except Exception,e:
        print 'Fehler bei:', c.getId(), o.getId(), e
        continue

     if refs:
        for r in refs:
            to = r.getTargetObject()
            print o.absolute_url(1), to.absolute_url(1), r.comment
      
return printed

