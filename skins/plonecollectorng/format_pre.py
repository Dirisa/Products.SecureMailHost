##parameters=text,cols=100

import textwrap

lst = []
for l in text.split('\n'):
    lst.extend(textwrap.wrap(l, cols))
return '\n'.join(lst)
