
# Dump all Archetypes references for backup purposes

for b in context.reference_catalog.searchResults():
    ref = b.getObject()
    print ref.getSourceObject().absolute_url(1),  ref.getTargetObject().absolute_url(1)

return printed

