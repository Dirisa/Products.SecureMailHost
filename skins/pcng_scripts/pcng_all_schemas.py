
# Show the schema settings for all PCNG instances within a folder
#
# Warning:
# Run this script from within a folder *containing* PloneCollectorNG
# instance but *not* on a PloneCollectorNG instance itself

collectors = context.objectValues('PloneCollectorNG')
fields = collectors[0].Schema().fields()

print '<table border="1">'
print '<tr>'
for field in fields: print '<th>%s</th>' % field.getName()
print '</tr>'

for c in collectors:
    schema = c.Schema()
    print '<tr>'
    for field in fields:
        print '<td>%s</td>' % schema[field.getName()].get(c)
    print '</tr>'

print '</table>'
return printed
