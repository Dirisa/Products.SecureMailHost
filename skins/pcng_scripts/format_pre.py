##parameters=fieldname,cols=100

import textwrap
accessor = getattr(context, 'get' + fieldname.capitalize())

#text = context.Schema()[fieldname].get(context)
text = accessor()
if same_type(text, u''):
    text = text.encode(context.getSiteEncoding())

lst = []
for l in text.split('\n'):
    lst.extend(textwrap.wrap(l, cols))
return '\n'.join(lst)
