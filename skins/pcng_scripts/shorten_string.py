##parameters=text, separator=' ', maxlength=60
# shorten a string

l = 0
lst = []

for f in text.split(separator):
    if l < maxlength:
        lst.append(f)
        l = l + len(f)
    else:
        return separator.join(lst) + ' ...'

return text
