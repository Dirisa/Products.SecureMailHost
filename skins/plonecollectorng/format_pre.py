##parameters=fieldname,cols=100

import textwrap

text = context.getField(fieldname).get(context)
if same_type(text, u''):
    text = text.encode(context.getSiteEncoding())

lst = []
for l in text.split('\n'):
    lst.extend(textwrap.wrap(l, cols))
return '\n'.join(lst)
