## Script (Python) "Check Selected"
##title=Check if a field should be 'selected' based on value and vocabulary
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=item, value

if value is not None and \
   unicode(repr(value)) == unicode(repr(item)):
    return 1

try:
    # Maybe repring?
    value.capitalize()
except AttributeError:
    # Maybe list?
    try:
        for v in value:
            if unicode(repr(item)) == unicode(repr(v)):
                return 1
    except TypeError:
        pass

return not not unicode(repr(value)) == unicode(repr(item))
