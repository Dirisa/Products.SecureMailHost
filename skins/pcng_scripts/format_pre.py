##parameters=fieldname,cols=100

import textwrap
#accessor = getattr(context, 'get' + fieldname.capitalize())
#accessor = context.getField(fieldname).accessor
text = context.Schema()[fieldname].getAccessor(context)()

#text = accessor()
if same_type(text, u''):
    text = text.encode(context.getSiteEncoding())

lst = []
for l in text.split('\n'):
    lst.extend(textwrap.wrap(l, cols))
return '\n'.join(lst)
