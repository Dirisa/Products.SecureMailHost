##parameters=text,cols=120,indent=0

# Wrap and indent text

from textwrap import wrap

if same_type(text, u''):
    text = text.encode(context.getSiteEncoding())

lst = []

for line in text.split('\n'):
    for l in wrap(line, int(cols)):
        lst.append(l)

if indent:
    for i in range(len(lst)):
        lst[i] = (' '*int(indent)) + lst[i]

return '\n'.join(lst)
