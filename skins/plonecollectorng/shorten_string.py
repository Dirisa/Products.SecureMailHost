##parameters=text='',seperator=' ',maxlength=40
# shorten a string

l = 0
lst = []

for f in text.split(seperator):

    if l < maxlength:
        lst.append(f)
        l = l + len(f)
    else:
        return seperator.join(lst) + ' ...'

return text
