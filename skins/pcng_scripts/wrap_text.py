##parameters=text,cols=80,indent=0, reencode=1

# Wrap and indent text

from textwrap import wrap

if same_type(text, u'') and reencode:
    text = text.encode(context.getSiteEncoding())

lst = []
for l in text.split('\n'):
    lst.extend(wrap(l, cols))

if indent:
    for i in range(len(lst)):
        lst[i] = (' '*int(indent)) + lst[i]

return '\n'.join(lst)
