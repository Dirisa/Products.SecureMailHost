import os
from Products.Archetypes.public import DisplayList

files = os.listdir(__path__[0])
files = [x for x in files if x.endswith('.py') and x not in ('__init__.py',)]

lst = []
for f in files:
    f = f[:-3]
    mod = __import__(f, globals(), globals(), __path__)
    k = '%s (%s)' % (mod.id, mod.title)
    v = '%s (%s)' % (mod.title, mod.id)
    lst.append((k,v))

VOC_WORKFLOWS = DisplayList(lst)
